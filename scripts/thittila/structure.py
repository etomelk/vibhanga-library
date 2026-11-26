#!/usr/bin/env python3
"""Write data/structure.json, the map of the Vibhaṅga: for every vibhaṅga its sections and
subsections, with the Pāli titles (data/pali.json), Thiṭṭila's English titles (data/thittila.json)
and the § range each covers. The Pāli and the English headings are paired in order.

    python3 scripts/thittila/structure.py"""
import json, os, re
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
CLOSER = re.compile(r'^\(Here Ends|is Ended$|^This is Called|^These are ')


def heads(chapters, english):
    out, last = [], None
    for c in chapters:
        for b in c['blocks']:
            if b['type'] == 'h':
                t = re.sub(r'⟨[^⟩]*⟩', '', b['text']).strip()
                if english and CLOSER.search(t):
                    continue
                out.append(dict(title=t, lvl=b.get('lvl'), first=None))
            elif b.get('pnum') is not None:
                for h in out:
                    if h['first'] is None:
                        h['first'] = b['pnum']
                out[-1]['_last'] = b['pnum']
    return out


def main():
    th = heads(json.load(open(os.path.join(ROOT, 'data', 'thittila.json'), encoding='utf-8'))['chapters'], True)
    last_done = max(h.get('_last', 0) for h in th)
    pali = json.load(open(os.path.join(ROOT, 'data', 'pali.json'), encoding='utf-8'))['chapters']
    pa = [h for h in heads(pali, False) if h['first'] is not None and h['first'] <= last_done]
    if len(pa) != len(th):
        raise SystemExit(f'headings do not pair: {len(pa)} Pāli, {len(th)} English')
    # the § where each heading's span ends: before the next heading of the same or a higher level
    ends = []
    for i, h in enumerate(th):
        nxt = next((x['first'] for x in th[i + 1:] if x['lvl'] <= h['lvl'] and x['first'] != h['first']), None)
        ends.append(nxt - 1 if nxt else last_done)
    vibs, stack = [], []
    for h, p, end in zip(th, pa, ends):
        node = dict(pali=p['title'], english=h['title'], paras=[h['first'], end], sections=[])
        while stack and stack[-1][0] >= h['lvl']:
            stack.pop()
        (stack[-1][1]['sections'] if stack else vibs).append(node)
        stack.append((h['lvl'], node))
    def prune(n):
        for s in n['sections']:
            prune(s)
        if not n['sections']:
            n.pop('sections')
    for v in vibs:
        prune(v)
    out = os.path.join(ROOT, 'data', 'structure.json')
    json.dump(dict(source='Pāli: data/pali.json; English: Thiṭṭila (data/thittila.json); paras = Vibhaṅga §',
                   through=last_done, vibhangas=vibs), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'wrote {out}: {len(vibs)} vibhaṅgas, {len(th)} headings, through §{last_done}')


if __name__ == '__main__':
    main()
