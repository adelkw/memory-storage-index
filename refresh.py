#!/usr/bin/env python3
"""Fetch the latest public Pricify weekly RAM/SSD/HDD JSON datasets."""
import json, urllib.request, datetime, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / 'data'
DATA.mkdir(exist_ok=True)
SOURCES = {
    'RAM': 'https://raw.githubusercontent.com/pricify-ai/pc-hardware-prices/main/latest/json/rams.live.json',
    'SSD': 'https://raw.githubusercontent.com/pricify-ai/pc-hardware-prices/main/latest/json/ssd.live.json',
    'HDD': 'https://raw.githubusercontent.com/pricify-ai/pc-hardware-prices/main/latest/json/hdd.live.json',
}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Memory-Storage-Index/1.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()

def main():
    stamp = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
    ok, errors = [], []
    for category, url in SOURCES.items():
        try:
            raw = fetch(url)
            doc = json.loads(raw.decode('utf-8'))
            if not isinstance(doc, dict) or not isinstance(doc.get('products'), list):
                raise ValueError('Unexpected data format; products list not found')
            (DATA / f'{category.lower()}.json').write_text(json.dumps(doc, ensure_ascii=False), encoding='utf-8')
            ok.append({'category': category, 'week': doc.get('week', 'not specified'), 'products': len(doc['products'])})
        except Exception as e:
            errors.append(f'{category}: {type(e).__name__}: {e}')
    state = {'checked_at': stamp, 'source': 'Pricify (pricify.ai)', 'license': 'CC BY 4.0', 'successful': ok, 'errors': errors}
    (DATA / 'status.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
    if ok:
        print('Refresh check completed.')
        for item in ok: print(f"{item['category']}: {item['products']} products — {item['week']}")
    if errors:
        print('Some sources could not be refreshed:')
        for e in errors: print(' - ' + e)
    if not ok:
        print('No new data was downloaded. Existing saved data, if any, has been kept.')
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
