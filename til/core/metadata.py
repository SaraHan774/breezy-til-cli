import json
import os
import time
from html.parser import HTMLParser
from typing import Dict, Optional, List
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# 캐시 및 네트워크 설정 상수 정의 (매직 넘버 방지)
CACHE_TTL_SECONDS: int = 60 * 60 * 24  # 24시간
CACHE_FILENAME: str = ".til_link_cache.json"
DEFAULT_TIMEOUT_SECONDS: int = 3
DEFAULT_USER_AGENT: str = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


class _OGHTMLParser(HTMLParser):
    """
    OG 메타데이터(og:title, og:description), 일반 description, title 태그, favicon 후보를 수집하는 파서
    """

    def __init__(self) -> None:
        super().__init__()
        self.og: Dict[str, str] = {}
        self.meta_name: Dict[str, str] = {}
        self.favicons: List[str] = []
        self._in_title: bool = False
        self.page_title: Optional[str] = None

    def handle_starttag(self, tag: str, attrs) -> None:
        # 태그 속성을 소문자 키 기반으로 접근하기 위해 변환한다.
        attr_dict = dict(attrs)
        lower = {k.lower(): v for k, v in attr_dict.items()}

        if tag.lower() == "meta":
            # og:*, name=description 등을 처리한다.
            prop = lower.get("property") or lower.get("name")
            content = attr_dict.get("content")
            if prop and content:
                if prop.startswith("og:"):
                    self.og[prop] = content.strip()
                elif prop.lower() == "description":
                    self.meta_name["description"] = content.strip()

        if tag.lower() == "link":
            # rel에 icon이 포함된 모든 링크를 favicon 후보로 추가한다.
            rel = lower.get("rel", "") or ""
            href = attr_dict.get("href")
            if href and ("icon" in rel.lower() or rel.lower() in {"shortcut icon", "apple-touch-icon"}):
                self.favicons.append(href)

        if tag.lower() == "title":
            self._in_title = True

    def handle_data(self, data: str) -> None:
        if self._in_title:
            text = (data or "").strip()
            if text:
                self.page_title = (self.page_title or "") + text

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False


def _load_cache(base_dir: str) -> Dict[str, dict]:
    """
    링크 메타데이터 캐시를 로드한다. 실패 시 빈 딕셔너리를 반환한다.
    """
    path = os.path.join(base_dir, CACHE_FILENAME)
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_cache(base_dir: str, cache: Dict[str, dict]) -> None:
    """
    링크 메타데이터 캐시를 저장한다. 저장 실패는 무시한다.
    """
    path = os.path.join(base_dir, CACHE_FILENAME)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        # 캐시 저장 실패는 기능에 영향을 주지 않으므로 조용히 무시한다.
        pass


def _origin_from_url(url: str) -> str:
    """
    주어진 URL에서 scheme과 netloc로 구성된 origin을 반환한다.
    """
    parsed = urlparse(url)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc
    return f"{scheme}://{netloc}"


def _choose_favicon(candidates: List[str], base_url: str) -> str:
    """
    파비콘 후보 리스트에서 첫 번째를 선택하고, 없으면 /favicon.ico로 폴백한다.
    상대 경로인 경우 절대 경로로 변환한다.
    """
    origin = _origin_from_url(base_url)
    if candidates:
        return urljoin(base_url, candidates[0])
    return urljoin(origin, "/favicon.ico")


def fetch_url_metadata(base_dir: str, url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> Dict[str, str]:
    """
    URL에서 og:title, og:description, favicon을 수집한다.
    - 캐시가 유효하면 캐시를 사용한다.
    - 네트워크/파싱 실패 시 빈 딕셔너리를 반환한다.

    반환 딕셔너리 키: title, description, favicon
    """
    # 캐시 확인
    cache = _load_cache(base_dir)
    now = int(time.time())
    entry = cache.get(url)
    if entry and isinstance(entry, dict):
        try:
            ts = int(entry.get("_ts", 0))
        except Exception:
            ts = 0
        if now - ts < CACHE_TTL_SECONDS:
            return {k: v for k, v in entry.items() if k != "_ts"}

    # 네트워크 요청 (타임아웃과 UA 설정)
    try:
        req = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
        with urlopen(req, timeout=timeout_seconds) as resp:
            content_type = resp.headers.get("Content-Type", "")
            # Content-Type이 비어 있거나 html을 포함하면 파싱 시도
            if content_type and ("html" not in content_type.lower()):
                return {}
            body = resp.read()
            # 인코딩은 헤더 기반으로 시도, 실패 시 utf-8로 디코딩
            try:
                encoding = resp.headers.get_content_charset() or "utf-8"
            except Exception:
                encoding = "utf-8"
            html = body.decode(encoding, errors="ignore")
    except Exception:
        return {}

    # HTML 파싱
    parser = _OGHTMLParser()
    try:
        parser.feed(html)
    except Exception:
        return {}

    # 제목/설명/파비콘 결정 로직 (우선순위 적용)
    title = parser.og.get("og:title") or parser.page_title or url
    description = parser.og.get("og:description") or parser.meta_name.get("description") or ""
    favicon = _choose_favicon(parser.favicons, url)

    result = {
        "title": title.strip(),
        "description": " ".join(description.strip().splitlines()).strip(),
        "favicon": favicon.strip(),
    }

    # 캐시 저장 (실패는 무시)
    try:
        cache[url] = {**result, "_ts": now}
        _save_cache(base_dir, cache)
    except Exception:
        pass

    return result


