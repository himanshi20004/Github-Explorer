import requests
import os
import base64
from urllib.parse import urlparse

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

IGNORE_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".pdf", ".zip", ".tar", ".gz", ".exe", ".bin", ".lock",
    ".woff", ".woff2", ".ttf", ".eot", ".mp4", ".mp3",
}

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "coverage", ".pytest_cache",
}

MAX_FILE_SIZE = 100_000  # 100KB per file


def parse_github_url(url: str):
    """Extract owner and repo from GitHub URL."""
    url = url.rstrip("/")
    parts = urlparse(url).path.strip("/").split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")
    return parts[0], parts[1]


def fetch_repo_tree(owner: str, repo: str):
    """Fetch the full file tree of the repo using Git Trees API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD?recursive=1"
    resp = requests.get(api_url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return data.get("tree", [])


def should_include_file(path: str) -> bool:
    """Filter out binary, large, and irrelevant files."""
    parts = path.split("/")
    for part in parts[:-1]:
        if part in IGNORE_DIRS:
            return False
    ext = os.path.splitext(path)[1].lower()
    if ext in IGNORE_EXTENSIONS:
        return False
    return True


def fetch_file_content(owner: str, repo: str, path: str) -> str | None:
    """Fetch a single file's content from GitHub API."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(api_url, headers=HEADERS)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("size", 0) > MAX_FILE_SIZE:
        return None
    if data.get("encoding") == "base64":
        try:
            return base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        except Exception:
            return None
    return None


def fetch_repo_files(github_url: str) -> list[dict]:
    """Main entry: fetch all text files from a GitHub repo."""
    owner, repo = parse_github_url(github_url)
    print(f"[Fetcher] Fetching tree for {owner}/{repo}...")
    tree = fetch_repo_tree(owner, repo)

    files = []
    blobs = [item for item in tree if item["type"] == "blob"]
    text_blobs = [b for b in blobs if should_include_file(b["path"])]

    print(f"[Fetcher] Found {len(text_blobs)} candidate files (filtered from {len(blobs)})")

    for item in text_blobs[:40]:  # cap at 80 files to avoid rate limits
        path = item["path"]
        content = fetch_file_content(owner, repo, path)
        if content and content.strip():
            files.append({"path": path, "content": content})
            print(f"[Fetcher] ✓ {path}")

    print(f"[Fetcher] Loaded {len(files)} files")
    return files, owner, repo