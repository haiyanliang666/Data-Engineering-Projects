from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen


def download_dataset(url: str, destination: str | Path) -> Path:
    """Download a dataset file for repeatable local ingestion."""
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url, timeout=60) as response:
            target.write_bytes(response.read())
    except Exception as exc:  # pragma: no cover - exact network errors vary by platform
        raise RuntimeError(f"Failed to download dataset from {url}") from exc
    return target
