# you-shall-not-pass

A daily log pipeline with data contracts and a quarantine layer, built on the BGL supercomputer log dataset.

> **Status: under active development.** Day-to-day work happens on the [`dev`](https://github.com/almeidaota/you-shall-not-pass/tree/dev) branch, where code, folder layout and commands may change or break between commits. `main` only gets a step once it runs end to end. Download and landing (one file per day) are done. Bronze, silver and gold are the plan, not working code yet.

## Why

Anomaly detectors for system logs are trained on data that is assumed to be clean. In practice it is not: logs can be dirty by accident (malformed lines, broken parsing, timezone mistakes) or on purpose (data poisoning). This project asks a simple question: **which layer of a data pipeline catches which kind of dirt?** A schema check stops a broken line, but a well-formed malicious line goes straight through.

## Related work

This project starts from LogPurge (Zhang et al., 2025), which removes anomalies from training logs before a detector learns from them. LogPurge was designed for accidental contamination and was evaluated on BGL (the dataset used here), Liberty and a private industrial dataset. The question this pipeline builds toward is what happens when the contamination is deliberate.

## Pipeline

```
BGL.log ──► landing ──► bronze ──► silver ──────► gold
            one file    raw lines   parsed +       template counts
            per day     + id        validated      per window
                                       │
                                       └──► quarantine
```

- **landing** (done): the simulated source. The full log is split into one file per day, so it looks like a system that delivers a new file every day.
- **bronze** (planned): raw lines with a stable id, one partition per day.
- **silver** (planned): lines parsed into templates and checked against a data contract; lines that fail go to quarantine.
- **gold** (planned): template counts per time window, ready for an anomaly detector.

Each day is stored as a Hive-style partition (`dt=YYYY-MM-DD/`), so a single day can be reprocessed without touching the others.

## Dataset

BGL, from the [Loghub](https://github.com/logpai/loghub) collection: logs from the BlueGene/L supercomputer at Lawrence Livermore National Laboratory, with each line labeled as alert or normal (`-` in the first column means normal).

- Source: [Zenodo record 8196385](https://zenodo.org/records/8196385), file `BGL.zip`
- 4,747,963 lines, from 2005-06-03 to 2006-01-04: 216 calendar days, 215 with data

**The log is not included in this repository.** Download it from the link above.

### Data notes

- **Which field defines the day:** the `Date` field (third column, e.g. `2005.06.03`), as written in the log, in the machine's local time, with no timezone conversion. The unix `Timestamp` field was not used.
- **Lines without a valid date:** none. Every line has a `Date` that maps to one of the 215 days (checked on 2026-11-20).
- **Missing day:** there are no lines on 2005-08-01, so the landing has 215 partitions, not 216.

## How to run

Requirements: Python 3.14 and [uv](https://docs.astral.sh/uv/).

Run everything from the repository root:

```bash
uv sync
uv run python main.py                # runs every step below, in order
```

Or one step at a time:

```bash
uv run python -m pipeline.download   # BGL.zip from Zenodo -> data/BGL.log, checks size and line count
uv run python -m pipeline.landing    # data/BGL.log -> data/landing/dt=YYYY-MM-DD/BGL.log
```

Both steps can be run again safely: the download skips a log that is already there and correct, and the landing rewrites each day with the same content.

To check the landing:

```bash
cat data/landing/dt=*/BGL.log | wc -l   # 4747963
command ls data/landing | wc -l         # 215
```

## Project layout

```
main.py              runs the whole pipeline
pipeline/
  config.py          shared paths (data/, BGL.log)
  download.py        downloads and checks the BGL log
  landing.py         splits the log into one file per day
data/                created by the scripts, not versioned
```

## Code style

- Code, comments and messages in English.
- PEP 8 names: `snake_case` for variables and functions, `UPPER_CASE` for constants.
- Names say what a thing is, not its type (`lines`, not `temp_df`).
- `pathlib.Path` for file paths, not strings.
- Type hints on function signatures.
- Each step lives in `pipeline/` and runs with `uv run python -m pipeline.<step>`.
- Before committing:

  ```bash
  uv run ruff format . && uv run ruff check .
  ```

## References

- Zhu, J., He, S., He, P., Liu, J., & Lyu, M. R. (2023). *Loghub: A Large Collection of System Log Datasets for AI-driven Log Analytics.* ISSRE 2023. [arXiv:2008.06448](https://arxiv.org/abs/2008.06448)
- Zhang, S., Chen, Z., Que, Z., Liu, Y., Sun, Y., Wei, S., Pei, D., & Li, H. (2025). *LogPurge: Log Data Purification for Anomaly Detection via Rule-Enhanced Filtering.* arXiv preprint, [arXiv:2511.14062](https://arxiv.org/abs/2511.14062)
- Oliner, A., & Stearley, J. (2007). *What Supercomputers Say: A Study of Five System Logs.* DSN 2007. [doi:10.1109/DSN.2007.103](https://doi.org/10.1109/DSN.2007.103)
