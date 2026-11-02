#!/usr/bin/env python3
"""Check a bounded UTF-8 CSV against an explicit header/count contract."""
import argparse
import csv
import hashlib
import io
import json
import stat
from pathlib import Path

LIMIT = 16 * 1024 * 1024


def load_bytes(path, limit):
    # Reject nonregular files before opening (ordinary CLI inputs, not hostile races).
    p = Path(path)
    if not stat.S_ISREG(p.stat().st_mode):
        raise ValueError('regular_file_required')
    with p.open('rb') as f:
        data = f.read(limit + 1)
    if len(data) > limit:
        raise ValueError('size_limit')
    return data


def unique_object(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise ValueError('duplicate_contract_key')
        d[k] = v
    return d


def contract_from(raw):
    c = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)
    if not isinstance(c, dict) or set(c) != {'header', 'rows', 'delimiter'}:
        raise ValueError('contract_fields')
    h = c['header']
    if (not isinstance(h, list) or not h or
            any(not isinstance(x, str) or not x for x in h) or
            len(set(h)) != len(h)):
        raise ValueError('contract_header')
    if type(c['rows']) is not int or c['rows'] < 0:
        raise ValueError('contract_rows')
    d = c['delimiter']
    if not isinstance(d, str) or len(d) != 1 or d in '\r\n"\x00':
        raise ValueError('contract_delimiter')
    return c


def check(raw, c):
    text = raw.decode('utf-8-sig')  # one optional UTF-8 BOM
    reader = csv.reader(io.StringIO(text, newline=''), delimiter=c['delimiter'],
                        quotechar='"', doublequote=True, strict=True)
    header = next(reader, None)
    count = 0
    width_errors = 0
    examples = []
    for count, row in enumerate(reader, 1):
        if len(row) != len(c['header']):
            width_errors += 1
            if len(examples) < 10:
                examples.append(count)
    issues = []
    if header != c['header']:
        issues.append('header_mismatch')
    if count != c['rows']:
        issues.append('record_count_mismatch')
    if width_errors:
        issues.append('record_width_mismatch')
    return {'status': 'mismatch' if issues else 'pass',
            'source_sha256': hashlib.sha256(raw).hexdigest(),
            'rows_observed': count, 'rows_expected': c['rows'],
            'width_error_count': width_errors,
            'first_width_error_records': examples, 'issues': issues}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('csv_file')
    p.add_argument('contract_file')
    a = p.parse_args(argv)
    try:
        c = contract_from(load_bytes(a.contract_file, 65536))
        report = check(load_bytes(a.csv_file, LIMIT), c)
        code = 0 if report['status'] == 'pass' else 1
    except (OSError, ValueError, csv.Error, RecursionError, OverflowError):
        # Never echo parser messages, paths, contracts, headers or cell values.
        report = {'status': 'error', 'issues': ['unreadable_invalid_or_oversize_input']}
        code = 2
    print(json.dumps(report, sort_keys=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
