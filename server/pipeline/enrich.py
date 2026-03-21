"""
URL / GitHub repo enrichment.

Fetches relevant content from a URL or GitHub repo and returns a concise
summary to prepend to the Claude prompt.
"""

import re
import httpx
from bs4 import BeautifulSoup


_GITHUB_REPO_RE = re.compile(
    r"https?://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/\s]+)"
)


async def enrich_prompt(prompt: str, url: str | None) -> str:
    """Return enriched prompt. If no URL, returns prompt unchanged."""
    if not url:
        return prompt

    context = await _fetch_context(url.strip())
    if not context:
        return prompt

    return f"{prompt}\n\n--- Context from {url} ---\n{context}"


async def _fetch_context(url: str) -> str:
    m = _GITHUB_REPO_RE.match(url)
    if m:
        return await _fetch_github_repo(m.group("owner"), m.group("repo"))
    return await _fetch_webpage(url)


async def _fetch_github_repo(owner: str, repo: str) -> str:
    """Fetch README + file tree summary from GitHub API."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    async with httpx.AsyncClient(timeout=15) as client:
        # README
        readme_text = ""
        try:
            r = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/readme",
                headers=headers,
            )
            if r.status_code == 200:
                import base64
                content = r.json().get("content", "")
                readme_text = base64.b64decode(content).decode("utf-8", errors="ignore")
                # Truncate long READMEs
                readme_text = readme_text[:3000]
        except Exception:
            pass

        # Top-level file tree
        tree_text = ""
        try:
            r = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents",
                headers=headers,
            )
            if r.status_code == 200:
                files = [item["name"] for item in r.json() if isinstance(item, dict)]
                tree_text = "Files: " + ", ".join(files[:30])
        except Exception:
            pass

    parts = []
    if tree_text:
        parts.append(tree_text)
    if readme_text:
        parts.append(f"README:\n{readme_text}")
    return "\n\n".join(parts)


async def _fetch_webpage(url: str) -> str:
    """Fetch and extract readable text from a webpage."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            r = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; explainer-bot/1.0)"},
            )
            r.raise_for_status()
    except Exception:
        return ""

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # Collapse blank lines and truncate
    lines = [l for l in text.splitlines() if l.strip()]
    return "\n".join(lines[:150])
