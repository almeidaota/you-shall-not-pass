"""Download the BGL log from Zenodo into data/ and check its size."""

import os
import urllib.request
import zipfile
from pathlib import Path

URL = "https://zenodo.org/records/8196385/files/BGL.zip?download=1"
ZIP_SIZE = 57_489_019
LOG_LINES = 4_747_963

DATA_DIR = Path("data")
ZIP_PATH = DATA_DIR / "BGL.zip"
LOG_PATH = DATA_DIR / "BGL.log"


def count_lines(path: Path) -> int:
    lines = 0
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            lines += chunk.count(b"\n")
    return lines


def download() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if LOG_PATH.exists() and count_lines(LOG_PATH) == LOG_LINES:
        print(f"{LOG_PATH} already there, nothing to do")
        return

    if not ZIP_PATH.exists() or ZIP_PATH.stat().st_size != ZIP_SIZE:
        print(f"downloading {URL}")
        tmp = ZIP_PATH.with_suffix(".zip.tmp")
        urllib.request.urlretrieve(URL, tmp)
        if tmp.stat().st_size != ZIP_SIZE:
            raise RuntimeError(f"expected {ZIP_SIZE} bytes, got {tmp.stat().st_size}")
        os.replace(tmp, ZIP_PATH)

    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extract("BGL.log", DATA_DIR)

    lines = count_lines(LOG_PATH)
    if lines != LOG_LINES:
        raise RuntimeError(f"expected {LOG_LINES} lines, got {lines}")
    print(f"{LOG_PATH}: {lines} lines")


if __name__ == "__main__":
    download()
