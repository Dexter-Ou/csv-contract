# CSV Contract 0.1.0 preview

Run the example from the extracted directory:

```sh
python3 csv_contract.py example.csv contract.json
```

Expected: exit 0, JSON status `pass`, `rows_observed` and `rows_expected` both 2. One quoted field spans two physical lines. The supplied contract is an example; specify your own expectations independently for real files.

The ten synthetic unittest methods passed on Linux/Python 3.12.15. To rerun: `python3 -m unittest -v`. Read README.md for parser, metadata and filesystem limitations. No installer, dependency download or service is required. To remove this tool, delete its extracted directory; retain any reports you need. Re-extract the same pinned ZIP to recover the tool.

Inventory (SHA-256; this release document excluded to avoid a self-hash):

```text
4ce4fdbcb2ce6bab8c7b05b7ffff000b646dddebf23250cd376ea2c7503aa1a3  LICENSE
ff6741a92dc797429dc9dc33346f437bce939fb06f5d08edd4c8eccde3251d9b  README.md
3d3382fdfdb6f2af4529cc1b393e1013d2ae64f5723b284d6bb8d8c620f0026b  contract.json
257ee4734f1e8a0bc2e86ba611b56adcc03dfaf37950873a0f0c06ea369c54b9  csv_contract.py
63f246d64a4e9b2c0db1ba3eeebd3c504786b36edb107e9f7e4e2ac5bd1f8177  example.csv
b579830594e9b07647095b71202dff435411a39c329b549a8595f3d033e307a7  test_csv_contract.py
```
