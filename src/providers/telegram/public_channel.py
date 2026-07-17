"""Fetch public Telegram channel posts without login."""

from __future__ import annotations

import html
import re
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TelegramPost:
    """A single Telegram post fetched from a public channel page."""

    text: str
    url: str


class TelegramPublicChannelProvider:
    """Fetch recent messages from a public Telegram channel page.

    This is intentionally lightweight for the MVP. It does not require an
    authenticated Telegram session, so it can operate against public channels.
    """

    def __init__(self, timeout_seconds: int = 30) -> None:
        self._timeout_seconds = timeout_seconds

    def collect_posts(self, channel: str, limit: int = 20) -> tuple[TelegramPost, ...]:
        channel_name = self._normalize_channel(channel)
        url = f"https://t.me/s/{channel_name}"
        page = self._fetch(url)
        blocks = re.findall(
            r'<div class="tgme_widget_message_text js-message_text"[^>]*>(.*?)</div>',
            page,
            flags=re.DOTALL,
        )
        posts: list[TelegramPost] = []
        for block in blocks[:limit]:
            text = self._strip_html(block)
            if text:
                posts.append(TelegramPost(text=text, url=url))
        return tuple(posts)

    def _fetch(self, url: str) -> str:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (SubForge)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout_seconds) as response:
                return response.read().decode("utf-8", errors="replace")
        except urllib.error.URLError as exc:
            raise RuntimeError(f"Unable to fetch Telegram channel page {url}: {exc}") from exc

    def _strip_html(self, value: str) -> str:
        cleaned = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return html.unescape(cleaned).strip()

    def _normalize_channel(self, channel: str) -> str:
        value = channel.strip()
        value = value.removeprefix("https://t.me/")
        value = value.removeprefix("http://t.me/")
        value = value.removeprefix("t.me/")
        value = value.removeprefix("https://t.me/s/")
        value = value.removeprefix("http://t.me/s/")
        value = value.removeprefix("t.me/s/")
        value = value.strip("/")
        return value
