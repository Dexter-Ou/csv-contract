# CSV Contract

Check a UTF-8 CSV's exact header/order, logical data-record count and record widths against expectations you specify independently. Requires Python 3.10+ standard library; MIT-licensed preview from Gong LLC. Tested on Linux with Python 3.12.15; other platforms and Python versions have not been tested.

Download this repository as a ZIP using GitHub’s Code menu, extract it into a trusted directory, and open a terminal in the extracted directory. No installation is needed.

```sh
python3 csv_contract.py example.csv contract.json
python3 -m unittest -v
```

The example passes with two records even though one quoted field spans two physical lines. A JSON report goes to stdout. Exit 0 means the declared checks passed; 1 means mismatch; 2 means unreadable, invalid or oversized input (including contract). Ordinary argument errors use argparse stderr. No input files are rewritten. Runtime code has no networking or dependency installation.

Contract requires exactly `header` (nonempty unique strings in exact order), `rows` (nonnegative integer) and `delimiter` (one character excluding newline, NUL or double quote). Expected rows exclude the header. Dialect uses double-quoted fields, doubled internal quotes, no escape character, no trimming/sniffing/skipping. One initial UTF-8 BOM is accepted. Blank records count and fail width checks. There is no data typing, repair, import, key uniqueness or database parser compatibility guarantee. Python's strict CSV mode does not reject every imaginable nonstandard quoting pattern.

CSV limit is 16 MiB, contract limit 64 KiB, field limit is Python's default CSV field-size limit. Regular trusted local files only; file replacement races are not protected. Entire CSV is held in memory. Reports omit header/cell values and paths, but include counts, first ten bad record indices (1-based after header), and SHA-256 of the checked bytes. Hashes/counts can still be sensitive; share deliberately. Mismatch reports contain a source hash; parse errors produce a generic error without a hash or partial success.

A passing report proves only those checks on those bytes: a wrong expected count, same-width corrupted values or an importer configured differently can still lose data. Source may change after checking; keep the checked snapshot and independently configure/verify the importer. No import command is executed or generated. This tool adds no sandbox for hostile local filesystem inputs.

See [RELEASE.md](RELEASE.md) for the release inventory and [LICENSE](LICENSE) for license terms. For bug reports, use this repository’s Issues page and include a minimal synthetic example, the command, Python version and expected versus observed result. Do not upload private CSV data. Support is best effort.
