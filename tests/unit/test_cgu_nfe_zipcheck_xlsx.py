"""ZIP validation and the stdlib XLSX writer/reader. Synthetic inputs only."""

import zipfile
from decimal import Decimal
from pathlib import Path

import pytest
from tests.helpers.cgu_nfe_synthetic import baseline_month

from sirta_api.adapters.ingest.cgu_nfe import xlsx
from sirta_api.adapters.ingest.cgu_nfe.zipcheck import looks_like_html, sha256_file, validate_zip

WAF_PAGE = (
    b"<!DOCTYPE html><html><head><title>Human Verification</title></head>"
    b"<body>awsWafCookieDomainList</body></html>"
)


def test_valid_zip_reports_hash_size_and_members(tmp_path: Path) -> None:
    path = tmp_path / "202401_NFe.zip"
    baseline_month(path)
    report = validate_zip(path)
    assert report.ok, report.reason
    assert report.sha256 == sha256_file(path)
    assert report.size == path.stat().st_size
    assert {m.name for m in report.members} == {
        "202401_NFe_NotaFiscal.csv",
        "202401_NFe_NotaFiscalItem.csv",
        "202401_NFe_NotaFiscalEvento.csv",
    }


def test_human_verification_page_is_not_a_zip(tmp_path: Path) -> None:
    path = tmp_path / "x.zip"
    path.write_bytes(WAF_PAGE)
    report = validate_zip(path)
    assert not report.ok
    assert report.reason == "pagina_html_no_lugar_do_zip"
    assert looks_like_html(WAF_PAGE)
    assert not looks_like_html(b"PK\x03\x04binary")


@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (b"", "arquivo_vazio"),
        (b"not a zip at all, plain text", "assinatura_zip_invalida"),
    ],
)
def test_bad_signature_and_empty_file(tmp_path: Path, content: bytes, reason: str) -> None:
    path = tmp_path / "x.zip"
    path.write_bytes(content)
    assert validate_zip(path).reason == reason


def test_missing_file(tmp_path: Path) -> None:
    assert validate_zip(tmp_path / "nope.zip").reason == "arquivo_ausente"


def test_truncated_zip_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "202401_NFe.zip"
    baseline_month(path)
    path.write_bytes(path.read_bytes()[:-60])
    report = validate_zip(path)
    assert not report.ok
    assert report.reason.startswith("zip_ilegivel")


def test_size_different_from_expected_is_invalid(tmp_path: Path) -> None:
    path = tmp_path / "202401_NFe.zip"
    baseline_month(path)
    report = validate_zip(path, expected_size=path.stat().st_size + 10)
    assert not report.ok
    assert report.reason.startswith("tamanho_diferente_do_esperado")


def test_corrupted_member_fails_crc(tmp_path: Path) -> None:
    path = tmp_path / "202401_NFe.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_STORED) as archive:
        archive.writestr("202401_NFe_NotaFiscal.csv", b"A" * 4000)
    data = bytearray(path.read_bytes())
    data[200] ^= 0xFF  # inside the stored payload
    path.write_bytes(bytes(data))
    report = validate_zip(path)
    assert not report.ok
    assert report.reason.startswith("crc_invalido")


@pytest.mark.parametrize("name", ["../evil.csv", "/abs.csv", "dir/../../evil.csv", "c:/evil.csv"])
def test_unsafe_member_names_are_refused(tmp_path: Path, name: str) -> None:
    path = tmp_path / "x.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(zipfile.ZipInfo(name), b"data")
    report = validate_zip(path)
    assert not report.ok
    assert report.reason.startswith("nome_de_membro_inseguro")


def test_zip_bomb_ratio_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "bomb.zip"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("a.csv", b"0" * 20_000_000)
    report = validate_zip(path)
    assert not report.ok
    assert report.reason.startswith("razao_de_compressao_suspeita")


# -- xlsx ------------------------------------------------------------------------------------
def test_xlsx_round_trip_keeps_text_numbers_and_blanks(tmp_path: Path) -> None:
    path = tmp_path / "t.xlsx"
    with xlsx.XlsxWriter(path) as book:
        rows = book.add_sheet(
            "Dados",
            iter(
                [
                    ["01012100", 12, xlsx.Money(123456), Decimal("2.5000"), None],
                    ["A & B <x>", -3, xlsx.Money(-5), Decimal(0), ""],
                    ["  espaco  ", 0, xlsx.Money(0), Decimal("1" * 20), "ok"],
                ]
            ),
            header=["NCM", "Itens", "Valor", "Qtd", "Obs"],
            title="Titulo",
            preface=[["Cobertura PARCIAL"]],
        )
        book.add_sheet("Outra", [["x"]], header=["h"])
    assert rows == 2 + 2 + 1 + 3  # title + blank, preface + blank, header, data
    sheets = xlsx.read_xlsx(path)
    assert list(sheets) == ["Dados", "Outra"]
    data = sheets["Dados"]
    assert data[0] == ["Titulo"]
    assert data[2] == ["Cobertura PARCIAL"]
    header_index = next(i for i, r in enumerate(data) if r[:1] == ["NCM"])
    first, second, third = data[header_index + 1 : header_index + 4]
    assert first[0] == "01012100"  # leading zero kept: it is text
    assert first[1:4] == ["12", "1234.56", "2.5000"]
    assert second[0] == "A & B <x>"
    assert second[2] == "-0.05"
    assert third[0] == "  espaco  "
    assert third[3] == "1" * 20  # beyond 15 digits is written as text, not rounded by Excel


def test_xlsx_refuses_more_rows_than_excel_allows(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(xlsx, "EXCEL_MAX_ROWS", 5)
    with pytest.raises(xlsx.SheetTooLarge):
        with xlsx.XlsxWriter(tmp_path / "t.xlsx") as book:
            book.add_sheet("S", ([i] for i in range(10)), header=["n"])


def test_sheet_names_are_validated(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        with xlsx.XlsxWriter(tmp_path / "t.xlsx") as book:
            book.add_sheet("x" * 32, [], header=["h"])
    with pytest.raises(ValueError):
        with xlsx.XlsxWriter(tmp_path / "t2.xlsx") as book:
            book.add_sheet("a/b", [], header=["h"])
