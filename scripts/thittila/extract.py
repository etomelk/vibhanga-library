#!/usr/bin/env python3
"""Read the Rhys Davids PDF (the abhidhamma.de LaTeX typesetting, 2021) as positioned lines.

    python3 scripts/rhysdavids/extract.py rd.pdf lines.json

The PDF draws each accent as a glyph of its own over or under its letter: the macron (¯)
before the letter, the dot below (.) and the dot above (˙) after it. A glyph is an accent
when it overlaps its letter horizontally (a full stop never does: it follows its letter);
it is combined with the letter into one Unicode character (ā ī ū ṭ ḍ ṇ ḷ ṃ ṅ …).
Every line is written with its position, its spans of text and each span's style
(roman, italic, bold, bold italic), size and baseline shift, so that parse.py can tell
the text (10.9 pt), the endnotes (10.0 pt), superscript note numbers (8 pt, raised),
the margin page marks ("p. 12", 8 pt, in the margin) and the running heads apart.
"""
import json
import sys
import unicodedata

import pdfplumber

MACRON = {'a': 'ā', 'i': 'ī', 'ı': 'ī', 'u': 'ū', 'e': 'ē', 'o': 'ō', 'A': 'Ā', 'I': 'Ī', 'U': 'Ū', 'E': 'Ē', 'O': 'Ō'}
DOT_BELOW = {'t': 'ṭ', 'd': 'ḍ', 'n': 'ṇ', 'l': 'ḷ', 'm': 'ṃ', 's': 'ṣ', 'h': 'ḥ', 'r': 'ṛ', 'T': 'Ṭ', 'D': 'Ḍ', 'N': 'Ṇ', 'L': 'Ḷ',
             'M': 'Ṃ', 'S': 'Ṣ', 'H': 'Ḥ', 'R': 'Ṛ'}
DOT_ABOVE = {'n': 'ṅ', 'm': 'ṁ', 'N': 'Ṅ', 'M': 'Ṁ', 's': 'ṡ'}
OTHER = {'´': '́', '`': '̀', 'ˆ': '̂', '¨': '̈', '˜': '̃', 'ˇ': '̌'}


def style(fontname):
    f = fontname.split('+')[-1]
    if f.startswith('LinLibertineTBI'):
        return 'bi'
    if f.startswith('LinLibertineTB'):
        return 'b'
    if f.startswith('LinLibertineTI'):
        return 'i'
    if 'goth' in f:
        return 'goth'
    return 'r'


def combine(chars):
    """Fold accent glyphs into the letters they sit on. Returns a new list of chars."""
    out = []
    used = set()
    for i, c in enumerate(chars):
        t = c['text']
        if t in ('¯', '˙', '.') or t in OTHER:
            # the letter this glyph overlaps (same line, horizontal overlap of at least half the glyph)
            cx = (c['x0'] + c['x1']) / 2
            best = None
            for j in range(max(0, i - 3), min(len(chars), i + 4)):
                if j == i:
                    continue
                d = chars[j]
                if not d['text'].isalpha() or abs(d['top'] - c['top']) > 6:
                    continue
                if d['x0'] - 0.3 <= cx <= d['x1'] + 0.3:
                    best = j
                    break
            if best is not None:
                b = chars[best]['text']
                table = {'¯': MACRON, '˙': DOT_ABOVE, '.': DOT_BELOW}.get(t)
                if t == '.' and (c['top'] - chars[best]['top'] < 1.5):
                    best = None          # level with the letter: a full stop overlapping by kerning, not a dot below
                elif table is not None and b in table:
                    chars[best] = dict(chars[best], text=table[b])
                    used.add(i)
                    continue
                elif t in OTHER:
                    chars[best] = dict(chars[best], text=unicodedata.normalize('NFC', b + OTHER[t]))
                    used.add(i)
                    continue
        out.append(i)
    return [chars[i] for i in out if i not in used]


def lines_of(page):
    chars = [c for c in page.chars if c['text'] != ' ']
    chars = combine(chars)
    # group into lines by baseline: the text first, then the small type (superscript note
    # numbers, margin page marks) joins the line it is raised above, or makes its own
    chars.sort(key=lambda c: (round(c['bottom']), c['x0']))
    lines = []
    def add(c, allow_raise):
        for ln in lines:
            d = ln['base'] - c['bottom']
            if abs(d) < 2.5 or (allow_raise and 0 < d < 6 and ln['x0'] - 40 < c['x0'] < ln['x1'] + 40):
                ln['chars'].append(c)
                ln['x0'] = min(ln['x0'], c['x0'])
                ln['x1'] = max(ln['x1'], c['x1'])
                return
        lines.append(dict(base=c['bottom'], x0=c['x0'], x1=c['x1'], chars=[c]))
    big = [c for c in chars if c['size'] > 8.5]
    small = [c for c in chars if c['size'] <= 8.5]
    for c in big:
        add(c, False)
    for c in small:
        add(c, True)
    out = []
    for ln in sorted(lines, key=lambda l: l['base']):
        allc = sorted(ln['chars'], key=lambda c: c['x0'])
        # the margin page marks ("p. 12", small type outside the text block) are kept apart
        marg = []
        for side in ([c for c in allc if c['size'] <= 8.5 and c['x0'] < 55], [c for c in allc if c['size'] <= 8.5 and c['x0'] > 366]):
            if ''.join(c['text'] for c in side).startswith('p'):
                marg = side                # small type in the margin that is not a page mark (endnote numbers) stays text
        cs = [c for c in allc if c not in marg] or allc
        main = max((round(c['size'], 1) for c in cs), key=lambda s: sum(1 for c in cs if round(c['size'], 1) == s))
        spans = []
        prev = None
        for c in cs:
            st = style(c['fontname'])
            size = round(c['size'], 1)
            sup = size < main - 1.5 and (ln['base'] - c['bottom']) > 0.8
            gap = prev is not None and c['x0'] - prev['x1'] > 0.15 * size
            key = (st, size, sup)
            if spans and spans[-1]['key'] == key and not (gap and c['x0'] - prev['x1'] > 12):
                spans[-1]['t'] += (' ' if gap else '') + c['text']
                spans[-1]['x1'] = round(c['x1'], 1)
            else:
                spans.append(dict(key=key, t=(' ' if gap and spans else '') + c['text'], x0=round(c['x0'], 1), x1=round(c['x1'], 1)))
            prev = c
        if marg and cs is not allc:
            spans.append(dict(key=('r', 8.0, False), t=''.join(c['text'] for c in marg).replace('p.', 'p. ').replace('  ', ' '),
                              x0=round(marg[0]['x0'], 1), x1=round(marg[-1]['x1'], 1)))
        out.append(dict(top=round(min(c['top'] for c in cs), 1), base=round(ln['base'], 1), x0=round(ln['x0'], 1), x1=round(ln['x1'], 1), size=main,
                        spans=[dict(t=s['t'], st=s['key'][0], sz=s['key'][1], sup=s['key'][2], x0=s['x0'], x1=s['x1']) for s in spans]))
    return out


def main():
    pdf = pdfplumber.open(sys.argv[1])
    pages = []
    for n, p in enumerate(pdf.pages, 1):
        pages.append(dict(n=n, lines=lines_of(p)))
    json.dump(pages, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
    print('pages', len(pages))


if __name__ == '__main__':
    main()
