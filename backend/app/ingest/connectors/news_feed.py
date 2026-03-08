"""
News feed connector — Google News RSS / NewsAPI.

Searches for each vendor name in recent news and returns raw articles.
"""
from __future__ import annotations

import logging
import urllib.parse
from datetime import datetime, timezone
from typing import Any

from app.ingest.connectors.base import BaseConnector, RawSignal

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
NEWS_API_URL = "https://newsapi.org/v2/everything"


class NewsFeedConnector(BaseConnector):
    source_name = "news_feed"
    _rate_limit_seconds = 30.0

    async def fetch(self, vendor_names: list[str]) -> list[RawSignal]:
        signals: list[RawSignal] = []
        if self.api_key:
            signals.extend(await self._fetch_newsapi(vendor_names))
        else:
            signals.extend(await self._fetch_google_rss(vendor_names))
        return signals

    async def _fetch_newsapi(self, vendor_names: list[str]) -> list[RawSignal]:
        try:
            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping NewsAPI fetch")
            return []

        signals: list[RawSignal] = []
        query = " OR ".join(f'"{name}"' for name in vendor_names[:5])  # NewsAPI has query limit

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    NEWS_API_URL,
                    params={
                        "q": query,
                        "apiKey": self.api_key,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": 20,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:
            logger.error("NewsAPI fetch error: %s", exc)
            return []

        for article in data.get("articles", []):
            text = f"{article.get('title', '')} {article.get('description', '')} {article.get('content', '')}"
            published = None
            if pub := article.get("publishedAt"):
                try:
                    published = datetime.fromisoformat(pub.replace("Z", "+00:00"))
                except ValueError:
                    pass

            vendor_hint = next(
                (name for name in vendor_names if name.lower() in text.lower()), None
            )
            signals.append(RawSignal(
                source=self.source_name,
                raw_text=text.strip(),
                url=article.get("url"),
                published_at=published,
                vendor_hint=vendor_hint,
                extra={"title": article.get("title", ""), "source": article.get("source", {})},
            ))

        return signals

    async def _fetch_google_rss(self, vendor_names: list[str]) -> list[RawSignal]:
        try:
            import xml.etree.ElementTree as ET  # noqa: N817

            import httpx  # type: ignore[import]
        except ImportError:
            logger.warning("httpx not installed — skipping Google RSS fetch")
            return []

        signals: list[RawSignal] = []

        for vendor_name in vendor_names[:10]:  # limit to 10 vendors per run
            query = urllib.parse.quote(f'"{vendor_name}" risk breach fraud')
            url = GOOGLE_NEWS_RSS.format(query=query)
            try:
                async with httpx.AsyncClient(timeout=10) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    root = ET.fromstring(resp.text)
                    items = root.findall(".//item")
                    for item in items[:5]:
                        title = item.findtext("title") or ""
                        desc = item.findtext("description") or ""
                        link = item.findtext("link") or ""
                        pub_str = item.findtext("pubDate") or ""
                        published: Any = None
                        if pub_str:
                            try:
                                from email.utils import parsedate_to_datetime
                                published = parsedate_to_datetime(pub_str).replace(tzinfo=timezone.utc)
                            except Exception:
                                pass
                        signals.append(RawSignal(
                            source=self.source_name,
                            raw_text=f"{title} {desc}".strip(),
                            url=link,
                            published_at=published,
                            vendor_hint=vendor_name,
                        ))
            except Exception as exc:
                logger.debug("Google RSS error for %s: %s", vendor_name, exc)

        return signals
