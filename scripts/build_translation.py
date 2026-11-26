#!/usr/bin/env python3
"""Make the draft English translations of the three commentaries into books of the library.

    python3 scripts/build_translation.py [mulatika-en anutika-en]

The translation of a book lives in data/translations/<pāli slug>/<part>.md, one file per part
of the Pāli book (00.md is part 0), written by hand:

    label: Introduction                          the part's label and title in the contents
    title: The Opening of the Book (Ganthārambhakathā)

    @0
    the English of block 0 of that part of data/<pāli slug>.json
    @1
    …

Every block of the Pāli part has its entry, in the same order, so that the English book has the
same paragraphs, headings, § numbers and page markers (⟨pg:12⟩) as the Pāli: the chips to the
other books, the search and the side-by-side view line up paragraph by paragraph. A translator's
note is set in the paragraph, in square brackets. A part with no file is left out of the book;
a block with no entry yet shows the Pāli, marked as not yet translated.

This writes data/<slug>.json and the book's line in data/library.json (its progress), then
renders the book with scripts/build.py.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOOKS = {'sammoha-en': 'sammoha', 'mulatika-en': 'mulatika', 'anutika-en': 'anutika'}


def read_part(path):
    head, blocks, cur = {}, {}, None
    for line in open(path, encoding='utf-8').read().split('\n'):
        m = re.match(r'^@(\d+)\s*$', line)
        if m:
            cur = int(m.group(1))
            blocks[cur] = []
            continue
        if cur is None:
            m = re.match(r'^(label|title):\s*(.+)$', line)
            if m:
                head[m.group(1)] = m.group(2).strip()
            continue
        blocks[cur].append(line)
    return head, {k: '\n'.join(v).strip() for k, v in blocks.items()}


def build(slug):
    src = BOOKS[slug]
    pali = json.load(open(os.path.join(ROOT, 'data', f'{src}.json'), encoding='utf-8'))
    tdir = os.path.join(ROOT, 'data', 'translations', src)
    chapters, done, total, problems = [], 0, 0, []
    for k, ch in enumerate(pali['chapters']):
        total += len(ch['blocks'])
        path = os.path.join(tdir, f'{k:02d}.md')
        if not os.path.exists(path):
            continue
        head, tr = read_part(path)
        extra = sorted(set(tr) - set(range(len(ch['blocks']))))
        if extra:
            problems.append(f'{src} part {k}: entries {extra} have no block in the Pāli')
        blocks = []
        for i, b in enumerate(ch['blocks']):
            nb = {x: y for x, y in b.items() if x != 'text'}
            en = tr.get(i, '')
            if en:
                done += 1
                # the page markers of the Pāli must all be in the English (they are anchors)
                for pg in re.findall(r'⟨pg:[^⟩]+⟩', b['text']):
                    if pg not in en:
                        problems.append(f'{src} part {k} block {i}: {pg} missing')
                        en = pg + ' ' + en
                nb['text'] = re.sub(r'"([^"\n]+)"', r'“\1”', en)     # straight quotes, curly
            else:
                nb['text'] = '[Not yet translated.] *' + b['text'].replace('*', '') + '*'
            blocks.append(nb)
        chapters.append({'num': ch['num'], 'label': head.get('label', ch.get('label', '')),
                         'title': head.get('title', ch.get('title', '')), 'blocks': blocks})
    out = {'chapters': chapters, 'glossary': []}
    json.dump(out, open(os.path.join(ROOT, 'data', f'{slug}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    lib_path = os.path.join(ROOT, 'data', 'library.json')
    lib = json.load(open(lib_path, encoding='utf-8'))
    if not chapters:
        print(f'{slug}: nothing translated yet')
        return
    if not any(b['slug'] == slug for b in lib['books']):        # the first part: the book joins the library
        lib['books'].append(json.load(open(os.path.join(ROOT, 'data', 'translations', 'entries.json'), encoding='utf-8'))[slug])
    meta = next(b for b in lib['books'] if b['slug'] == slug)
    nparts = len(pali['chapters'])
    pct = round(100 * done / total) if total else 0
    meta['progress'] = f'{len(chapters)} of {nparts} parts, {pct}% of the text'
    meta['note'] = re.sub(r'<b class="progress">[^<]*</b>', f'<b class="progress">Translated so far: {meta["progress"]}.</b>', meta['note'])
    json.dump(lib, open(lib_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    open(lib_path, 'a', encoding='utf-8').write('\n')
    for p in problems:
        print('  !', p)
    print(f'{slug}: {len(chapters)} of {nparts} parts, {done} of {total} blocks ({pct}%)')
    if chapters:
        subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'build.py'), slug], check=True)


for s in (sys.argv[1:] or BOOKS):
    build(s)
