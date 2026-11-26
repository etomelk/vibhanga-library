#!/usr/bin/env python3
"""Print a part of the Pāli with block numbers, for translating:
   python3 scripts/translation/show.py mulatika 3 [from] [to]"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
slug, part = sys.argv[1], int(sys.argv[2])
a = int(sys.argv[3]) if len(sys.argv) > 3 else 0
z = int(sys.argv[4]) if len(sys.argv) > 4 else 10 ** 6
ch = json.load(open(os.path.join(ROOT, 'data', f'{slug}.json'), encoding='utf-8'))['chapters'][part]
words = sum(len(b['text'].split()) for b in ch['blocks'])
print('##', ch['num'], ch['label'], '|', ch['title'], '| blocks', len(ch['blocks']), '| words', words)
for i, b in enumerate(ch['blocks']):
    if a <= i < z:
        ex = {k: v for k, v in b.items() if k not in ('text', 'type')}
        print(f"@{i} [{b['type']}{(' ' + str(ex)) if ex else ''}] {b['text']}\n")
