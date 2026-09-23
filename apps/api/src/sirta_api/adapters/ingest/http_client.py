import re
import ssl
from dataclasses import dataclass
from pathlib import Path
from time import sleep
from urllib.parse import unquote

import certifi
import httpx

USER_AGENT = "SIRTA-official-ingest/0.3.43"
TRUST_DIR = Path(__file__).resolve().parent / "trust"


def official_ssl_context() -> ssl.SSLContext:
    """Trust store plus intermediates omitted by some official portals.

    Roots stay in certifi. The extra PEMs are public CA intermediates
    (Sectigo R36 and GlobalSign GCC R3 DV TLS CA 2020) required to complete
    the chain for dados.ba.gov.br and sefaz.ma.gov.br.
    """
    context = ssl.create_default_context(cafile=certifi.where())
    for pem in sorted(TRUST_DIR.glob("*.pem")):
        context.load_verify_locations(cafile=str(pem))
    return context


@dataclass(frozen=True)
class OfficialHttpResponse:
    url: str
    status_code: int
    body: bytes
    etag: str | None
    last_modified: str | None
    content_type: str | None


class OfficialHttpClient:
    def fetch(self, url: str, *, timeout: float = 120.0, retries: int = 3) -> OfficialHttpResponse:
        headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                with httpx.Client(
                    timeout=timeout,
                    follow_redirects=True,
                    headers=headers,
                    verify=official_ssl_context(),
                ) as client:
                    response = client.get(url)
                    if response.status_code >= 500 and attempt < retries - 1:
                        sleep(0.4 * (2**attempt))
                        continue
                    return OfficialHttpResponse(
                        url=str(response.url),
                        status_code=response.status_code,
                        body=response.content,
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                        content_type=response.headers.get("Content-Type"),
                    )
            except httpx.HTTPError as exc:
                last_error = exc
                sleep(0.4 * (2**attempt))
        if last_error is not None:
            raise last_error
        raise RuntimeError("official HTTP fetch exhausted retries")

    def fetch_post(
        self,
        url: str,
        *,
        data: dict[str, str],
        headers: dict[str, str] | None = None,
        timeout: float = 120.0,
        retries: int = 3,
        cookies: dict[str, str] | None = None,
    ) -> OfficialHttpResponse:
        base_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json,*/*",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        if headers:
            base_headers.update(headers)
        last_error: Exception | None = None
        for attempt in range(retries):
            try:
                with httpx.Client(
                    timeout=timeout,
                    follow_redirects=True,
                    headers=base_headers,
                    cookies=cookies or {},
                    verify=official_ssl_context(),
                ) as client:
                    response = client.post(url, data=data)
                    if response.status_code >= 500 and attempt < retries - 1:
                        sleep(0.4 * (2**attempt))
                        continue
                    return OfficialHttpResponse(
                        url=str(response.url),
                        status_code=response.status_code,
                        body=response.content,
                        etag=response.headers.get("ETag"),
                        last_modified=response.headers.get("Last-Modified"),
                        content_type=response.headers.get("Content-Type"),
                    )
            except httpx.HTTPError as exc:
                last_error = exc
                sleep(0.4 * (2**attempt))
        if last_error is not None:
            raise last_error
        raise RuntimeError("official HTTP POST exhausted retries")

    def fetch_csrf_form_post(
        self,
        *,
        page_url: str,
        post_url: str,
        form_data: dict[str, str],
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        """GET HTML page for CSRF cookie/meta, then POST form to official endpoint."""
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers=headers,
            verify=official_ssl_context(),
        ) as client:
            page = client.get(page_url)
            if page.status_code >= 400:
                return OfficialHttpResponse(
                    url=str(page.url),
                    status_code=page.status_code,
                    body=page.content,
                    etag=page.headers.get("ETag"),
                    last_modified=page.headers.get("Last-Modified"),
                    content_type=page.headers.get("Content-Type"),
                )
            html = page.text
            csrf = ""
            marker = 'name="csrf-token" content="'
            start = html.find(marker)
            if start >= 0:
                start += len(marker)
                end = html.find('"', start)
                if end > start:
                    csrf = html[start:end]
            xsrf = unquote(page.cookies.get("XSRF-TOKEN") or "")
            payload = dict(form_data)
            if csrf:
                payload.setdefault("_token", csrf)
            post_headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/json,*/*",
                "Content-Type": "application/x-www-form-urlencoded",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": page_url,
            }
            if csrf:
                post_headers["X-CSRF-TOKEN"] = csrf
            if xsrf:
                post_headers["X-XSRF-TOKEN"] = xsrf
            response = client.post(post_url, data=payload, headers=post_headers)
            return OfficialHttpResponse(
                url=str(response.url),
                status_code=response.status_code,
                body=response.content,
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
                content_type=response.headers.get("Content-Type"),
            )

    def fetch_primefaces_datatable(
        self,
        *,
        home_url: str,
        page_url: str,
        tax_code: str,
        year: str,
        date_start: str,
        date_end: str,
        rows: int = 1000,
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        """GET JSF session pages, consult Repasse WEB, expand DataTable rows, return HTML."""
        headers = {"User-Agent": USER_AGENT, "Accept": "text/html,*/*"}
        with httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers=headers,
            verify=official_ssl_context(),
        ) as client:
            home = client.get(home_url)
            if home.status_code >= 400:
                return OfficialHttpResponse(
                    url=str(home.url),
                    status_code=home.status_code,
                    body=home.content,
                    etag=home.headers.get("ETag"),
                    last_modified=home.headers.get("Last-Modified"),
                    content_type=home.headers.get("Content-Type"),
                )
            page = client.get(page_url)
            if page.status_code >= 400:
                return OfficialHttpResponse(
                    url=str(page.url),
                    status_code=page.status_code,
                    body=page.content,
                    etag=page.headers.get("ETag"),
                    last_modified=page.headers.get("Last-Modified"),
                    content_type=page.headers.get("Content-Type"),
                )
            view_state = _jsf_view_state(page.text)
            ajax_headers = {
                "User-Agent": USER_AGENT,
                "Accept": "application/xml, text/xml, */*",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Faces-Request": "partial/ajax",
                "Referer": page_url,
            }
            if tax_code != "1":
                change = client.post(
                    page_url,
                    data={
                        "javax.faces.partial.ajax": "true",
                        "javax.faces.source": "j_idt19:console",
                        "javax.faces.partial.execute": "j_idt19:console",
                        "javax.faces.partial.render": "j_idt19:filtrosGrid",
                        "javax.faces.behavior.event": "change",
                        "javax.faces.partial.event": "change",
                        "j_idt19:j_idt21": "j_idt19:j_idt21",
                        "j_idt19:console": tax_code,
                        "javax.faces.ViewState": view_state,
                    },
                    headers=ajax_headers,
                )
                view_state = _jsf_view_state(change.text) or view_state
            consult = client.post(
                page_url,
                data={
                    "javax.faces.partial.ajax": "true",
                    "javax.faces.source": "j_idt19:j_idt43",
                    "javax.faces.partial.execute": "@all",
                    "javax.faces.partial.render": ("j_idt19:panelGroupRepasse j_idt19:mensagem"),
                    "j_idt19:j_idt43": "j_idt19:j_idt43",
                    "j_idt19:j_idt21": "j_idt19:j_idt21",
                    "j_idt19:console": tax_code,
                    "j_idt19:anoSelect": year,
                    "j_idt19:j_idt27": "99999",
                    "j_idt19:dataInicial_input": date_start,
                    "j_idt19:dataFinal_input": date_end,
                    "javax.faces.ViewState": view_state,
                },
                headers=ajax_headers,
            )
            view_state = _jsf_view_state(consult.text) or view_state
            expanded = client.post(
                page_url,
                data={
                    "javax.faces.partial.ajax": "true",
                    "javax.faces.source": "j_idt19:j_idt46",
                    "javax.faces.partial.execute": "j_idt19:j_idt46",
                    "javax.faces.partial.render": "j_idt19:j_idt46",
                    "javax.faces.behavior.event": "page",
                    "javax.faces.partial.event": "page",
                    "j_idt19:j_idt46_pagination": "true",
                    "j_idt19:j_idt46_first": "0",
                    "j_idt19:j_idt46_rows": str(max(1, int(rows))),
                    "j_idt19:j_idt46_encodeFeature": "true",
                    "j_idt19:j_idt21": "j_idt19:j_idt21",
                    "j_idt19:console": tax_code,
                    "j_idt19:anoSelect": year,
                    "j_idt19:j_idt27": "99999",
                    "j_idt19:dataInicial_input": date_start,
                    "j_idt19:dataFinal_input": date_end,
                    "javax.faces.ViewState": view_state,
                },
                headers=ajax_headers,
            )
            table_html = _largest_cdata_block(expanded.text) or _largest_cdata_block(consult.text)
            body = (table_html or expanded.text or consult.text).encode("utf-8")
            return OfficialHttpResponse(
                url=page_url,
                status_code=expanded.status_code,
                body=body,
                etag=expanded.headers.get("ETag"),
                last_modified=expanded.headers.get("Last-Modified"),
                content_type=expanded.headers.get("Content-Type"),
            )


def _jsf_view_state(payload: str) -> str:
    match = re.search(
        r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
        payload or "",
    )
    if match:
        return match.group(1)
    match = re.search(
        r"ViewState[^>]*>\s*<!\[CDATA\[([^\]]+)\]\]>",
        payload or "",
    )
    return match.group(1) if match else ""


def _largest_cdata_block(payload: str) -> str:
    blocks = re.findall(r"<!\[CDATA\[([\s\S]*?)\]\]>", payload or "")
    if not blocks:
        return ""
    return max(blocks, key=len)


class SnapshotHttpClient:
    def __init__(self, payloads: dict[str, OfficialHttpResponse]) -> None:
        self._payloads = payloads

    def fetch(self, url: str, *, timeout: float = 120.0, retries: int = 3) -> OfficialHttpResponse:
        if url in self._payloads:
            return self._payloads[url]
        for prefix, payload in self._payloads.items():
            if url.startswith(prefix):
                return payload
        raise LookupError(f"no official snapshot registered for {url}")

    def fetch_post(
        self,
        url: str,
        *,
        data: dict[str, str],
        headers: dict[str, str] | None = None,
        timeout: float = 120.0,
        retries: int = 3,
        cookies: dict[str, str] | None = None,
    ) -> OfficialHttpResponse:
        return self.fetch(url, timeout=timeout, retries=retries)

    def fetch_csrf_form_post(
        self,
        *,
        page_url: str,
        post_url: str,
        form_data: dict[str, str],
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        return self.fetch(post_url, timeout=timeout)

    def fetch_primefaces_datatable(
        self,
        *,
        home_url: str,
        page_url: str,
        tax_code: str,
        year: str,
        date_start: str,
        date_end: str,
        rows: int = 1000,
        timeout: float = 120.0,
    ) -> OfficialHttpResponse:
        return self.fetch(page_url, timeout=timeout)
