"""Prompt DLP checks. Blocks obvious PII and secret material in AI prompts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

_CPF_RE = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
_CNPJ_RE = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")
_BEARER_RE = re.compile(r"bearer\s+[A-Za-z0-9\-_\.=]+", re.IGNORECASE)
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN (?:RSA )?PRIVATE KEY-----")


class DlpDecision(StrEnum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class DlpResult:
    allowed: bool
    decision: DlpDecision
    reason: str


def scan_prompt(text: str) -> DlpResult:
    if not text or not text.strip():
        return DlpResult(True, DlpDecision.ALLOW, "empty")
    if _PRIVATE_KEY_RE.search(text):
        return DlpResult(False, DlpDecision.BLOCK, "private key material detected")
    if _BEARER_RE.search(text):
        return DlpResult(False, DlpDecision.BLOCK, "bearer token or secret-like material detected")
    if _CPF_RE.search(text):
        return DlpResult(False, DlpDecision.BLOCK, "personal identifier (CPF-like) detected")
    if _CNPJ_RE.search(text):
        return DlpResult(False, DlpDecision.BLOCK, "personal identifier (CNPJ-like) detected")
    return DlpResult(True, DlpDecision.ALLOW, "no dlp hit")
