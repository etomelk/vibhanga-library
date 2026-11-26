#!/usr/bin/env python3
"""Render compare/: two books side by side, kept at the same place as either one is read.

compare/index.html      the page (shared/compare.js does the work)
compare/<slug>.json     for one book, its places that line up with a place in another book:
                        {"ids": [element ids in reading order],
                         "to": {other slug: [[index into ids, id in the other book], ...]}}

The places come from the links the books already carry:
  - the chips to the other books beside a section (a.xb: §594 in Khine → §594 in the Pāli),
  - the PTS page markers of the Expositor (a.ptsp → the page of the Aṭṭhasālinī),
  - the mātikā items of every book (data/concordance.json: t1 in Dhammajeewa → t1 in Khine).
Where two books have no link between them (the Expositor and the Pāli text), the way goes
through a third book that has links to both (Expositor → Aṭṭhasālinī page → its § → Pāli §).

Run it after a book is rebuilt:

    python3 scripts/build_compare.py
"""
import bisect
import html
import json
import os
import re

import lxml.html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = lambda s: html.escape(s, quote=False)
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))
_spec = open(os.path.join(ROOT, 'scripts', 'build_home.py'), encoding='utf-8').read()
SHELVES = eval(re.search(r'^SHELVES = (\[.*?^\])', _spec, re.S | re.M).group(1))
shelf_of = {s: k for k, (_, _, ss) in enumerate(SHELVES) for s in ss}
books = sorted(lib['books'], key=lambda b: (shelf_of[b['slug']], SHELVES[shelf_of[b['slug']]][2].index(b['slug'])))
SLUGS = [b['slug'] for b in books]
HUBS = ['pali', 'sammoha']     # the books a way may go through, in this order

# the book each one opens beside, unless the reader picks another
PARTNER = {'thittila': 'pali', 'pali': 'thittila', 'sammoha': 'pali', 'mulatika': 'mulatika-en', 'anutika': 'anutika-en', 'sammoha-en': 'sammoha', 'mulatika-en': 'mulatika', 'anutika-en': 'anutika'}
# a translation made paragraph by paragraph: every id of one is the same place in the other
PARALLEL = {'sammoha-en': 'sammoha', 'mulatika-en': 'mulatika', 'anutika-en': 'anutika'}

order = {}      # slug -> [ids in reading order]
chap = {}       # slug -> [chapter id of each of those]
pos = {}        # slug -> {id: position}
links = {s: {} for s in SLUGS}   # slug -> {other: {id: target id}}   (first link of an element wins)

for s in SLUGS:
    page = lxml.html.fromstring(open(os.path.join(ROOT, s, 'index.html'), encoding='utf-8').read())
    ids, chs = [], []
    for sec in page.xpath('//section[contains(concat(" ",@class," ")," chapter ")]'):
        ids.append(sec.get('id'))
        chs.append(sec.get('id'))
        src = sec.get('data-src')
        frag = lxml.html.fromstring('<div>' + open(os.path.join(ROOT, s, src), encoding='utf-8').read() + '</div>') if src else sec
        for el in frag.iter():
            if not isinstance(el.tag, str):
                continue
            i = el.get('id')
            if i and el is not frag:
                ids.append(i)
                chs.append(sec.get('id'))
            if el.tag == 'a':
                m = re.match(r'\.\./([a-z]+)/#(.+)$', el.get('href') or '')
                if not m or m.group(1) not in links or m.group(1) == s:
                    continue
                src_el = el
                while src_el is not None and not src_el.get('id'):
                    src_el = src_el.getparent()
                if src_el is None or src_el is frag:
                    continue
                links[s].setdefault(m.group(1), {}).setdefault(src_el.get('id'), m.group(2))
    order[s] = ids
    chap[s] = chs
    pos[s] = {}
    for k, i in enumerate(ids):
        pos[s].setdefault(i, k)

for t, p in PARALLEL.items():
    if t in pos and p in pos:
        for i in order[t]:
            if i in pos[p]:
                links[t].setdefault(p, {}).setdefault(i, i)
                links[p].setdefault(t, {}).setdefault(i, i)

# the mātikā items, in every book that sets them out
_cf = os.path.join(ROOT, 'data', 'concordance.json')
conc = json.load(open(_cf, encoding='utf-8')) if os.path.exists(_cf) else {'books': {}}
for a, items in conc['books'].items():
    for b, items_b in conc['books'].items():
        if a == b or a not in links or b not in links:
            continue
        for item, x in items.items():
            y = items_b.get(item)
            if y and x.get('item') and y.get('item') and x['item'] in pos[a] and y['item'] in pos[b]:
                links[a].setdefault(b, {}).setdefault(x['item'], y['item'])


def pairs(a, b):
    """[(position in a, id in b)] in a's reading order, direct links only."""
    out = [(pos[a][i], t) for i, t in links[a].get(b, {}).items() if i in pos[a] and t in pos[b]]
    return sorted(out)


direct = {(a, b): pairs(a, b) for a in SLUGS for b in SLUGS if a != b}


def at_or_before(ps, p, s):
    """the target of the last pair at or before position p in book s, if it is in the same part"""
    k = bisect.bisect_right(ps, (p, '￿')) - 1
    return ps[k][1] if k >= 0 and chap[s][ps[k][0]] == chap[s][p] else None


report = []
os.makedirs(os.path.join(ROOT, 'compare'), exist_ok=True)
for a in SLUGS:
    to = {}
    for b in SLUGS:
        if a == b:
            continue
        ps = list(direct[(a, b)])
        via = ''
        have = {p for p, _ in ps}
        for h in HUBS:
            if h in (a, b) or not direct[(a, h)] or not direct[(h, b)]:
                continue
            # where a links to h but not to b, go on from h to b
            add = []
            for p, hid in direct[(a, h)]:
                if p in have:
                    continue
                t = at_or_before(direct[(h, b)], pos[h][hid], h)
                if t:
                    add.append((p, t))
                    have.add(p)
            if add:
                via += (' + ' if via else '') + f'{len(add)} via {h}'
                ps += add
        ps.sort()
        if ps:
            to[b] = ps
        report.append((a, b, len(direct[(a, b)]), via))
    used = sorted({p for ps in to.values() for p, _ in ps})
    index = {p: k for k, p in enumerate(used)}
    chs = list(dict.fromkeys(chap[a][p] for p in used))
    data = {'ids': [order[a][p] for p in used],
            'chs': chs, 'c': [chs.index(chap[a][p]) for p in used],
            'to': {b: [[index[p], t] for p, t in ps] for b, ps in to.items()}}
    with open(os.path.join(ROOT, 'compare', f'{a}.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

# ---- the page
meta = [{'slug': b['slug'], 'cite': b.get('cite', b['author']), 'title': b['title'],
         'partner': PARTNER.get(b['slug'], 'pali' if b['slug'] != 'pali' else 'sammoha')} for b in books]
tpl = open(os.path.join(ROOT, 'scripts', 'compare.html'), encoding='utf-8').read()
page = (tpl.replace('{{TITLE}}', e(lib['title']))
           .replace('{{DATA}}', json.dumps({'books': meta}, ensure_ascii=False).replace('</', '<\\/')))
open(os.path.join(ROOT, 'compare', 'index.html'), 'w', encoding='utf-8').write(page)

none = [(a, b) for a, b, n, v in report if not n and not v]
print(f'wrote compare/: {len(SLUGS)} books, {sum(1 for _, _, n, v in report if n or v)} of {len(report)} pairs lined up')
if os.environ.get('VERBOSE'):
    for a, b, n, v in report:
        print(f'  {a:12} → {b:12} {n:5} direct {v}')
for a, b in none:
    print(f'  no way from {a} to {b}')
