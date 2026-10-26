"""Fetch Open Bandit data files and verify SHA-256 checksums."""

import argparse
import hashlib
import urllib.request
from pathlib import Path

PINNED_COMMIT_SHA = "8cbd5fa4558b7ad2ba4781546d6604e4cc3e07c4"

SAMPLE_FILES = {
    "men_random_10k": (
        "obd/random/men/men.csv",
        f"https://raw.githubusercontent.com/st-tech/zr-obp/{PINNED_COMMIT_SHA}/obd/random/men/men.csv",
    ),
    "men_bts_10k": (
        "obd/bts/men/men.csv",
        f"https://raw.githubusercontent.com/st-tech/zr-obp/{PINNED_COMMIT_SHA}/obd/bts/men/men.csv",
    ),
}

EXPECTED_SHA256 = {
    "random_men_10k": "ede6d08c6877f99cd3770f7d09e26c738e6aa6de4445ccccfb1356ba5d06b1eb",
    "bts_men_10k": "db6d1f7ed2d591ba521533e45286d4c1fba7fe57a8ad2e80342210335f43c527",
}


def file_sha256(path: Path) -> str:
    """Return the hex SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path, expected_sha256: str | None = None) -> str:
    """Download a file and verify its SHA-256 when an expectation is given.

    Args:
        url: Remote URL to download from.
        dest: Local destination path.
        expected_sha256: Expected hex SHA-256; download fails on mismatch.

    Returns:
        The actual hex SHA-256 of the downloaded file.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)
    actual = file_sha256(dest)
    if expected_sha256 is not None and actual != expected_sha256:
        raise ValueError(f"sha256 mismatch for {url}: expected {expected_sha256}, got {actual}")
    return actual


def fetch_samples() -> None:
    """Fetch the pinned 10k-row samples and verify their checksums."""
    for name, (_repo_path, url) in SAMPLE_FILES.items():
        dest = Path("data") / f"{name}.csv"
        actual = fetch(url, dest, EXPECTED_SHA256.get(name))
        print(f"{name}: {actual}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true", help="fetch full data instead of samples")
    args = parser.parse_args()
    if args.full:
        raise NotImplementedError("full data fetch requires url and sha256 at Phase 0 sign-off")
    fetch_samples()


if __name__ == "__main__":
    main()
