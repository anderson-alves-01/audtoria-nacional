"""CLI of the CGU NF-e pipeline.

    python -m sirta_api.adapters.ingest.cgu_nfe status
    python -m sirta_api.adapters.ingest.cgu_nfe inventory --probe
    python -m sirta_api.adapters.ingest.cgu_nfe download --concurrency 2
    python -m sirta_api.adapters.ingest.cgu_nfe import-zip C:\\Downloads\\202402_NFe.zip
    python -m sirta_api.adapters.ingest.cgu_nfe process
    python -m sirta_api.adapters.ingest.cgu_nfe audit
    python -m sirta_api.adapters.ingest.cgu_nfe export
    python -m sirta_api.adapters.ingest.cgu_nfe reconcile-reference
    python -m sirta_api.adapters.ingest.cgu_nfe resume

Everything is idempotent: a validated ZIP is not downloaded again and a month already processed with
the same SHA-256 and processing version is not processed again. Each invocation has a ``run_id``.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

from sirta_api.adapters.ingest.cgu_nfe import acquire as acquire_mod
from sirta_api.adapters.ingest.cgu_nfe.export import Exporter, ExportError
from sirta_api.adapters.ingest.cgu_nfe.inventory import (
    CatalogUnavailable,
    make_client,
    month_statuses,
    refresh_inventory,
)
from sirta_api.adapters.ingest.cgu_nfe.process import process_month
from sirta_api.adapters.ingest.cgu_nfe.reference import load_reference, reconcile_reference
from sirta_api.adapters.ingest.cgu_nfe.store import Store
from sirta_api.config import get_settings
from sirta_api.domain.cgu_nfe import (
    PROCESSING_VERSION,
    STATE_DONE,
    STATE_VALIDATED,
    CguNfeError,
    is_month,
    requested_months,
)

DEFAULT_REFERENCE_ZIP = Path("docs/data/CGU_2021_2025_Detalhamento_PARCIAL.zip")
DEFAULT_REFERENCE_XLSX = Path("docs/data/CGU_2021_2025_PARCIAL.xlsx")


def _months(args: argparse.Namespace) -> list[str]:
    if args.months:
        bad = [m for m in args.months if not is_month(m)]
        if bad:
            raise SystemExit(f"mês inválido (use AAAAMM): {', '.join(bad)}")
        return sorted(set(args.months))
    selected = requested_months()
    if args.since:
        selected = [m for m in selected if m >= args.since]
    if args.until:
        selected = [m for m in selected if m <= args.until]
    return selected


def _reference_hashes(path: Path | None) -> dict[str, str] | None:
    candidate = path or DEFAULT_REFERENCE_ZIP
    if candidate.is_file():
        try:
            return load_reference(candidate, detail=False).hashes
        except CguNfeError:
            return None
    return None


def _print_status(store: Store, months: list[str]) -> Counter:
    counts: Counter = Counter()
    for s in month_statuses(store, months):
        counts[s.state] += 1
        head = f"HEAD {s.head_status}" if s.head_status else "HEAD -"
        size = f" {s.head_size / 1e6:.1f} MB" if s.head_size else ""
        extra = f"  {s.detail}" if s.detail else ""
        print(f"{s.month}  {s.state:<24} {head}{size}{extra}")
    print("--")
    for state, n in sorted(counts.items()):
        print(f"{state}: {n}")
    return counts


def cmd_status(store: Store, args: argparse.Namespace) -> int:
    _print_status(store, _months(args))
    return 0


def cmd_inventory(store: Store, args: argparse.Namespace) -> int:
    months = _months(args)
    with make_client(timeout=args.timeout) as client:
        try:
            refresh_inventory(store, client, probe=args.probe, months=months)
        except CatalogUnavailable as error:
            print(f"catálogo indisponivel: {error}", file=sys.stderr)
            return 2
    _print_status(store, months)
    if args.out:
        _write_inventory(store, months, Path(args.out))
    return 0


def _write_inventory(store: Store, months: list[str], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["mes", "estado", "listado", "url", "head_http", "head_bytes", "detalhe", "sha256"]
        )
        for s in month_statuses(store, months):
            writer.writerow(
                [
                    s.month,
                    s.state,
                    int(s.listed),
                    s.url,
                    s.head_status,
                    s.head_size,
                    s.detail,
                    s.sha256,
                ]
            )


def cmd_download(store: Store, args: argparse.Namespace) -> int:
    months = _months(args)
    reference = _reference_hashes(Path(args.reference_zip) if args.reference_zip else None)
    with make_client(timeout=args.timeout) as client:
        try:
            if not args.no_catalog:
                refresh_inventory(store, client, probe=False, months=requested_months())
        except CatalogUnavailable as error:
            print(f"catálogo indisponivel: {error}", file=sys.stderr)
            return 2
        listed = {s.month for s in month_statuses(store, months) if s.listed}
        targets = [m for m in months if m in listed or store.current_file(m)]
        for m in months:
            if m not in targets:
                print(f"{m}  NAO_LISTADO (não tentado)")
        downloader = acquire_mod.Downloader(
            store,
            client,
            retries=args.retries,
            backoff=args.backoff,
            breaker_limit=args.breaker,
            pause=args.pause,
            reference_hashes=reference,
        )
        results = downloader.download_many(targets, concurrency=args.concurrency, force=args.force)
    tally: Counter = Counter()
    for r in sorted(results, key=lambda x: x.month):
        tally[r.outcome] += 1
        print(f"{r.month}  {r.outcome:<20} HTTP {r.http_status or '-'}  {r.detail}")
    print("--")
    for outcome, n in sorted(tally.items()):
        print(f"{outcome}: {n}")
    blocked = tally.get(acquire_mod.OUTCOME_BLOCKED, 0)
    if blocked:
        print(
            "Bloqueio de verificação humana registrado e NAO contornado. Baixe os ZIPs oficiais "
            "no navegador e use `import-zip`."
        )
    return 3 if blocked or tally.get(acquire_mod.OUTCOME_INVALID, 0) else 0


def cmd_import_zip(store: Store, args: argparse.Namespace) -> int:
    reference = _reference_hashes(Path(args.reference_zip) if args.reference_zip else None)
    status = 0
    for name in args.paths:
        result = acquire_mod.import_zip(
            store, Path(name), month=args.month, reference_hashes=reference
        )
        flag = "ACEITO" if result.accepted else "RECUSADO"
        match = ""
        if result.reference_match is not None:
            match = f"  igual a referência={'SIM' if result.reference_match else 'NAO'}"
        print(f"{flag}  {result.month or '?'}  {result.detail}  sha256={result.sha256}{match}")
        status = status or (0 if result.accepted else 1)
    return status


def cmd_process(store: Store, args: argparse.Namespace) -> int:
    failures = 0
    for month in _months(args):
        if store.current_file(month) is None:
            continue
        outcome = process_month(store, month, force=args.force)
        if outcome.status == "ERRO":
            failures += 1
        counts = outcome.counts
        summary = (
            f"notas={counts.get('notas_aceitas')} itens={counts.get('itens_aceitos')} "
            f"quarentena={counts.get('quarentena')}"
            if counts
            else outcome.detail
        )
        print(f"{month}  {outcome.status:<14} {summary}")
    return 1 if failures else 0


def cmd_audit(store: Store, args: argparse.Namespace) -> int:
    rows = store.conn.execute(
        "SELECT month, check_id, resultado, quantidade, detalhe FROM auditoria "
        "ORDER BY month, resultado, check_id"
    ).fetchall()
    tally: Counter = Counter(r["resultado"] for r in rows)
    for r in rows:
        if r["resultado"] in ("FALHA", "ALERTA"):
            print(
                f"{r['month']}  {r['resultado']:<7} {r['check_id']}  {r['quantidade']}  "
                f"{r['detalhe']}"
            )
    print("--", dict(tally))
    states = Counter(s.state for s in month_statuses(store))
    print("estados:", dict(states))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle, delimiter=";")
            writer.writerow(["mes", "verificacao", "resultado", "quantidade", "detalhe"])
            writer.writerows([tuple(r) for r in rows])
    return 1 if tally.get("FALHA") else 0


def cmd_export(store: Store, args: argparse.Namespace) -> int:
    exporter = Exporter(store, prefix=args.prefix)
    try:
        report = exporter.run(Path(args.out_dir) if args.out_dir else None)
    except ExportError as error:
        print(f"exportação recusada: {error}", file=sys.stderr)
        return 2
    kind = "PARCIAL" if report.partial else "COMPLETO"
    print(
        f"{kind}: {len(report.months_done)} meses processados; "
        f"pendentes: {len(report.months_pending)}"
    )
    print(f"{report.workbook.path}  sha256={report.workbook.sha256}")  # type: ignore[union-attr]
    for f in report.csv_files:
        print(f"{f.path}  linhas={f.rows}  sha256={f.sha256}")
    for check, result, detail in report.checks:
        print(f"[{result}] {check}: {detail}")
    return 0 if report.ok else 1


def cmd_reconcile_reference(store: Store, args: argparse.Namespace) -> int:
    reference = load_reference(
        Path(args.reference_zip or DEFAULT_REFERENCE_ZIP),
        xlsx_path=Path(args.reference_xlsx or DEFAULT_REFERENCE_XLSX),
    )
    report = reconcile_reference(store, reference)
    lines = [f"run_id={store.run_id}", *report.summary, ""]
    lines += [
        f"{r.month}  {r.state:<24} ref={r.reference:<28} local={r.local:<40} hash={r.hash_match}  "
        f"{r.verdict}"
        for r in report.rows
    ]
    print("\n".join(lines))
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0


def cmd_resume(store: Store, args: argparse.Namespace) -> int:
    """Download what is pending, process what is validated, report what is missing."""
    status = cmd_download(store, args)
    pending_process = [
        s.month for s in month_statuses(store, _months(args)) if s.state == STATE_VALIDATED
    ]
    if pending_process:
        args.months = pending_process
        status = max(status, cmd_process(store, args))
    print("resumo final:")
    _print_status(store, requested_months())
    done = sum(1 for s in month_statuses(store) if s.state == STATE_DONE)
    print(f"{done} de {len(requested_months())} meses com processamento concluido")
    return status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cgu_nfe", description=__doc__.splitlines()[0])
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", help="pasta do datalake (padrão: <datalake_root>/cgu-nfe)")
    common.add_argument("--months", nargs="+", metavar="AAAAMM", help="meses específicos")
    common.add_argument("--since", metavar="AAAAMM")
    common.add_argument("--until", metavar="AAAAMM")
    common.add_argument("--reference-zip", help="pacote de referência anterior (hashes)")
    common.add_argument("--reference-xlsx", help="planilha de referência anterior (valores)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", parents=[common]).set_defaults(func=cmd_status)

    p = sub.add_parser(
        "inventory", help="lê o catálogo e, com --probe, faz HEAD por mês", parents=[common]
    )
    p.add_argument("--probe", action="store_true")
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--out")
    p.set_defaults(func=cmd_inventory)

    def download_options(p: argparse.ArgumentParser) -> None:
        p.add_argument("--concurrency", type=int, default=2)
        p.add_argument("--retries", type=int, default=3)
        p.add_argument(
            "--backoff", type=float, default=2.0, help="segundos, dobra a cada tentativa"
        )
        p.add_argument("--timeout", type=float, default=120.0)
        p.add_argument("--breaker", type=int, default=3, help="bloqueios seguidos que param tudo")
        p.add_argument(
            "--pause", type=float, default=5.0, help="segundos de pausa apos cada arquivo"
        )
        p.add_argument("--force", action="store_true")
        p.add_argument("--no-catalog", action="store_true", help="não reler o catálogo")

    p = sub.add_parser("download", help="baixa os meses listados, com retomada", parents=[common])
    download_options(p)
    p.set_defaults(func=cmd_download)

    p = sub.add_parser(
        "import-zip", help="importa ZIP oficial obtido manualmente", parents=[common]
    )
    p.add_argument("paths", nargs="+")
    p.add_argument("--month", metavar="AAAAMM", help="obrigatório se o nome não tiver o mês")
    p.set_defaults(func=cmd_import_zip)

    p = sub.add_parser("process", help="processa os ZIPs validados", parents=[common])
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_process)

    p = sub.add_parser("audit", parents=[common])
    p.add_argument("--out")
    p.set_defaults(func=cmd_audit)

    p = sub.add_parser("export", help="XLSX de seis abas e CSVs completos", parents=[common])
    p.add_argument("--prefix", default="CGU_NFE_2021_2025")
    p.add_argument("--out-dir")
    p.set_defaults(func=cmd_export)

    p = sub.add_parser("reconcile-reference", parents=[common])
    p.add_argument("--out")
    p.set_defaults(func=cmd_reconcile_reference)

    p = sub.add_parser("resume", help="download + process dos pendentes", parents=[common])
    download_options(p)
    p.set_defaults(func=cmd_resume)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root) if args.root else Path(get_settings().datalake_root) / "cgu-nfe"
    store = Store(root)
    print(f"run_id={store.run_id}  versão={PROCESSING_VERSION}  raiz={root}")
    try:
        return int(args.func(store, args))
    except CguNfeError as error:
        print(f"erro: {error}", file=sys.stderr)
        return 1
    finally:
        store.close()


if __name__ == "__main__":
    raise SystemExit(main())
