# Verdict 0.3.97

## Slice

Activate BCB OLINDA ExpectativasMercadoInflacao12Meses and
ExpectativasMercadoInflacao24Meses (FOCUS_INFLACAO_12M/24M / Suavizada)
PUBLIC_OPEN.

## Checks

- Unit: `test_bcb_olinda_expectativas_parses_inflacao_12m_suavizada`,
  `test_bcb_olinda_expectativas_parses_inflacao_24m_suavizada`, sectoral panel count 12
- Integration: Inflacao12m/24m ingest gold lineage without credit; alembic head `0100`
- Migration: `0100_bcb_olinda_inflacao_12_24m` -> implementation_version `0.3.97`
- Probe SHA-256 (12m): `4508D554756ABF90F927F43E1FEBE91E42333008A9B91C3BEA4498AC45F01CC0` (1654 bytes)
- Probe SHA-256 (24m): `478E262B260D1F489AC3D03A2614513A86A73C37ACEA69ECA2B87DC4BDDD3440` (1696 bytes)
- Median samples: IPCA 12m N=4.8016; IPCA 24m N=3.9081 (Data 2026-09-18)

## Constraints preserved

- No tax credit from public enrichment data
- Gold `REAL_OFFICIAL_DATA_PENDING_HUMAN_VALIDATION`
- No national load; fixture-minimized only
- Distinct from annual/monthly/trimestral Focus and Selic Copom
