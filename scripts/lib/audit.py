"""Library corrections checked against the Pāli sources: each becomes ⟦new|printed|audit|source⟧ in the text,
which build.py shows as the corrected words, marked, with the printed words and the source on hover or tap.

An entry: find (the text around the change; it must occur at place `nth`, not counting text inside earlier
corrections), old (the printed words inside `find`; empty for an addition), new (empty for a removal),
ref (the source, shown to the reader), before (for an addition: put it before this text in `find`;
otherwise after `find`)."""
import re

MARK = re.compile(r'⟦[^⟧]*⟧')


def mark(new, old, ref):
    for x in (new, old, ref):
        assert '|' not in x and '⟦' not in x and '⟧' not in x, x
    return f'⟦{new}|{old}|audit|{ref}⟧'


def free_spans(s):
    """the stretches of s outside earlier corrections"""
    out, i = [], 0
    for m in MARK.finditer(s):
        out.append((i, m.start()))
        i = m.end()
    out.append((i, len(s)))
    return out


def locate(s, find):
    for a, b in free_spans(s):
        k = s.find(find, a)
        while k != -1 and k + len(find) <= b:
            yield k
            k = s.find(find, k + 1)


def apply_one(s, k, e):
    find, old, new = e['find'], e.get('old', ''), e.get('new', '')
    if e.get('remark'):         # a word inside an earlier correction: that correction is replaced (printed word kept)
        m = MARK.search(s, k)
        printed = m.group(0)[1:-1].split('|')[1]
        return s[:m.start()] + mark(new, printed, e['ref']) + s[m.end():]
    if old:
        j = k + find.index(old)
        printed = re.sub(r'\s*\[sic\]', '', old)        # Nhu Lien: the proofread's [sic] mark is not part of the print
        return s[:j] + mark(new, printed, e['ref']) + s[j + len(old):]
    j = k + (find.index(e['before']) if e.get('before') else len(find))
    return s[:j] + mark(new, '', e['ref']) + (' ' if e.get('cell') else '') + s[j:]   # cell: fills an empty table cell


def apply_all(slots, entries, where=''):
    """slots: a list of [get, set] pairs over the book's strings, in reading order."""
    missing = []
    for e in entries:
        n = e.get('nth', 0)
        done = False
        for get, put in slots:
            s = get()
            hits = [s.find(e['find'])] if e.get('remark') and e['find'] in s else ([] if e.get('remark') else list(locate(s, e['find'])))
            if n < len(hits):
                put(apply_one(s, hits[n], e))
                done = True
                break
            n -= len(hits)
        if not done:
            missing.append(e['find'])
    if missing:
        raise SystemExit(f'{where}: {len(missing)} corrections not found:\n  ' + '\n  '.join(missing))
    return len(entries)


def string_slots(obj):
    """[get, set] for every string inside nested dicts and lists, in order"""
    out = []

    def walk(o):
        items = o.items() if isinstance(o, dict) else enumerate(o)
        for k, v in items:
            if isinstance(v, str):
                out.append((lambda o=o, k=k: o[k], lambda x, o=o, k=k: o.__setitem__(k, x)))
            elif isinstance(v, (dict, list)):
                walk(v)
    walk(obj)
    return out


def check_pages(text_dir, entries_by_page):
    """apply {page: [entries]} to the pages in text_dir; print each correction in its context"""
    import os
    n = 0
    for pg, entries in sorted(entries_by_page.items()):
        raw = open(os.path.join(text_dir, pg + '.md'), encoding='utf-8').read()
        box = [raw]
        apply_all([(lambda: box[0], lambda x: box.__setitem__(0, x))], entries, pg)
        for m in MARK.finditer(box[0]):
            a = box[0].rfind('\n', 0, m.start()) + 1
            print(pg, '…' + box[0][max(a, m.start() - 50):m.start()] + m.group(0) + box[0][m.end():m.end() + 30].split('\n')[0])
            n += 1
        for e in entries:
            for x in (e.get('old', ''), e.get('new', '')):
                assert ' | ' not in x and '\n' not in x, (pg, x)
    print(n, 'corrections')
