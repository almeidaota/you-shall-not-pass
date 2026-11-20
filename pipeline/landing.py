from pathlib import Path

import polars as pl

from pipeline.config import DATA_DIR, LOG_PATH

COLUMNS_NAMES = [
    "line",
    "Label",
    "Timestamp",
    "Date",
]


def read_bgl_log() -> pl.DataFrame:
    df = pl.read_lines(LOG_PATH)
    df = df.with_columns((pl.col("line").str.splitn(" ", 4)).alias("new_line")).unnest(
        "new_line"
    )
    new_cols_name = {key: value for key, value in zip(df.columns, COLUMNS_NAMES)}
    df = df.rename(new_cols_name)
    return df


def split_by_date(df: pl.DataFrame, landing_dir: Path) -> None:
    df_split_by_date = df.partition_by("Date", as_dict=True)
    for key, df_date in df_split_by_date.items():
        day = key[0].replace(".", "-")

        lines = df_date.select(pl.col("line")).to_series().to_list()
        directory = landing_dir / f"dt={day}"
        directory.mkdir(parents=True, exist_ok=True)

        with open(directory / "BGL.log", "w", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")


def split() -> None:
    bgl_log = read_bgl_log()
    split_by_date(bgl_log, DATA_DIR / "landing")


if __name__ == "__main__":
    split()
