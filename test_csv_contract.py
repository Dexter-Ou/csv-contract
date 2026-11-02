import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('csv_contract.py')
CONTRACT = {'header': ['id', 'note'], 'rows': 2, 'delimiter': ','}
GOOD = b'id,note\n1,"two\nlines"\n2,ok\n'


class Journey(unittest.TestCase):
    def run_case(self, raw, contract=CONTRACT):
        with tempfile.TemporaryDirectory() as d:
            f, c = Path(d)/'data.csv', Path(d)/'contract.json'
            f.write_bytes(raw)
            c.write_text(json.dumps(contract), encoding='utf-8')
            r = subprocess.run([sys.executable, str(SCRIPT), str(f), str(c)],
                               capture_output=True, timeout=10)
            self.assertEqual(f.read_bytes(), raw)
            self.assertEqual(r.stderr, b'')
            return r.returncode, json.loads(r.stdout)

    def test_multiline_and_hash(self):
        code, r = self.run_case(GOOD)
        self.assertEqual(code, 0)
        self.assertEqual(r['rows_observed'], 2)
        self.assertEqual(r['source_sha256'], hashlib.sha256(GOOD).hexdigest())

    def test_prefix_not_silently_skipped(self):
        code, r = self.run_case(b'export metadata\n'+GOOD)
        self.assertEqual(code, 1)
        self.assertIn('header_mismatch', r['issues'])
        self.assertIn('record_count_mismatch', r['issues'])

    def test_order_exact(self):
        code, r = self.run_case(GOOD.replace(b'id,note', b'note,id'))
        self.assertEqual((code, r['issues']), (1, ['header_mismatch']))

    def test_truncated_export(self):
        code, r = self.run_case(b'id,note\n1,only\n')
        self.assertEqual((code, r['issues']), (1, ['record_count_mismatch']))

    def test_width_without_value_disclosure(self):
        code, r = self.run_case(b'id,note\n1,PRIVATE_MARKER,extra\n2,ok\n')
        self.assertEqual(code, 1)
        self.assertEqual(r['first_width_error_records'], [1])
        self.assertNotIn('PRIVATE_MARKER', json.dumps(r))

    def test_invalid_utf8_and_unclosed_quote(self):
        for raw in [b'\xff', b'id,note\n1,"PRIVATE_MARKER']:
            code, r = self.run_case(raw)
            self.assertEqual(code, 2)
            self.assertNotIn('PRIVATE_MARKER', json.dumps(r))

    def test_contract_validation(self):
        for patch in [{'rows': True}, {'header': ['id', 'id']}, {'skip': 1},
                      {'delimiter': '\n'}, {'rows': -1}]:
            c = dict(CONTRACT, **patch)
            code, _ = self.run_case(GOOD, c)
            self.assertEqual(code, 2)

    def test_bom_semicolon_crlf_empty(self):
        c = dict(CONTRACT, delimiter=';')
        code, _ = self.run_case(b'\xef\xbb\xbfid;note\r\n1;yes\r\n2;ok\r\n', c)
        self.assertEqual(code, 0)
        code, r = self.run_case(b'')
        self.assertEqual(code, 1)
        self.assertIn('header_mismatch', r['issues'])

    def test_blank_record_not_ignored(self):
        code, r = self.run_case(GOOD + b'\n')
        self.assertEqual(code, 1)
        self.assertEqual(r['rows_observed'], 3)
        self.assertEqual(r['width_error_count'], 1)

    def test_size_limit(self):
        code, _ = self.run_case(b'x' * (16*1024*1024+1))
        self.assertEqual(code, 2)


if __name__ == '__main__':
    unittest.main()
