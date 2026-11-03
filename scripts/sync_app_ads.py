"""Combine publisher-owned entries with the current CAS list."""
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://raw.githubusercontent.com/cleveradssolutions/App-ads.txt/main/app-ads.txt'


def merge(custom, cas):
    if not cas.startswith('# CAS.ai Updated') or 'OwnerDomain=cas.ai' not in cas:
        raise ValueError('Unexpected CAS response; leaving app-ads.txt unchanged')
    records = [line for line in cas.splitlines() if ',' in line and not line.startswith('#')]
    if len(records) < 1000:
        raise ValueError('CAS list looks truncated; leaving app-ads.txt unchanged')
    seen = set()
    output = []
    for line in (custom.rstrip() + '\n\n' + cas.rstrip()).splitlines():
        value = line.split('#', 1)[0].strip()
        if ',' in value:
            parts = [part.strip() for part in value.split(',')]
            key = (parts[0].lower(), *parts[1:])
            if key in seen:
                continue
            seen.add(key)
        output.append(line)
    return '\n'.join(output) + '\n'


if __name__ == '__main__':
    with urlopen(URL, timeout=60) as response:
        cas = response.read().decode('utf-8-sig')
    result = merge((ROOT / 'app-ads-custom.txt').read_text(), cas)
    target = ROOT / 'app-ads.txt'
    temporary = target.with_suffix('.tmp')
    temporary.write_bytes(result.replace('\n', '\r\n').encode('utf-8'))
    temporary.replace(target)
