"""Offline consistency checks; does not call any model or execute generated code."""
from pathlib import Path
import csv
import hashlib
import json
import statistics

root = Path(__file__).resolve().parent.parent
provenance = json.loads((root / 'provenance.json').read_text())
for item in provenance['files']:
    path = root / item['published']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['published_sha256'], path
runs = json.loads((root / 'run-summary.json').read_text())
cases = json.loads((root / 'case-results.json').read_text())
assert len(runs) == 21
assert len(cases) == 684
assert sum(r['total'] for r in runs) == len(cases)
for run in runs:
    source = json.loads((root / run['source']).read_text())
    if 'results' in source:
        rows = [r for r in source['results'] if r['case'] not in ('warmup', 'multi_step')]
        passed = sum(bool(r.get('checks', {}).get('pass')) for r in rows)
        strict = passed
    else:
        rows = source['cases']
        passed = sum(bool(r['pass']) for r in rows)
        strict = sum(bool(r['strict_pass']) for r in rows)
    assert (len(rows), passed, strict) == (run['total'], run['passed'], run['strict_passed']), run['source']
    assert abs(statistics.median(r['seconds'] for r in rows) - run['median_seconds']) < 0.000001
with (root / 'case-results.csv').open() as stream:
    assert len(list(csv.DictReader(stream))) == len(cases)
with (root / 'run-summary.csv').open() as stream:
    assert len(list(csv.DictReader(stream))) == len(runs)
for path in root.rglob('*.json'):
    json.loads(path.read_text())
    assert str(Path.home()) not in path.read_text(), path
settings = json.loads((root / 'environment/current.json').read_text())
assert all(m['native_context_tokens'] == m['configured_context_tokens'] for m in settings['models'])
print(f'OK: {len(runs)} runs, {len(cases)} cases, {len(provenance["files"])} source artifacts; hashes and native context settings verified.')
