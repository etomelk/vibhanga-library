#!/usr/bin/env python3
"""Build data/thittila.json from the lines of Thiṭṭila's Book of Analysis (scripts/thittila/extract.py).

    python3 scripts/thittila/parse.py work/lines.json [first_pdf_page last_pdf_page]

What the PDF shows, and what it becomes:
- the running head (top of the page) and the page number at the foot: dropped;
- "p. 12" in the margin, with a "|" in the line where the page turned: the page of the printed
  translation (PTS 1969), an anchor ⟨pg:12⟩ at the "|";
- "[**12**]" in the text: the page of the PTS Pāli edition (Rhys Davids 1904), ⟨pg:P12⟩, the same
  pages that the Pāli reader marks P;
- "12. " at the start of a paragraph: the Sixth Council paragraph number (pnum), as in the Pāli;
- bold and italic spans: **…** and *…*;
- the small lines (9 pt) under a paragraph ("P = See para. 154."): notes of the translator, kept
  in place as indented lines;
- headings: 24.8 pt (a vibhaṅga), 14.3 pt (a section), 12 pt (a subsection);
- a word broken at a line end is joined; its hyphen is kept only where the book writes the
  word with a hyphen inside a line more often than without.
Parts follow the parts of the Pāli reader (data/pali.json), so both are cut at the same §."""
import collections
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
BODY = 10.9
FIRST_TEXT_PAGE = 91          # the PDF page where the translation begins (book p. 1)
LAST_TEXT_PAGE = 678
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')     # the note marks after :P: (P¹ = see para. …)


def span_text(s):
    t = s['t']
    if not t.strip():
        return t
    lead = t[:len(t) - len(t.lstrip())]
    trail = t[len(t.rstrip()):]
    core = t.strip()
    if s['st'] == 'b':
        return f'{lead}**{core}**{trail}'
    if s['st'] == 'i':
        return f'{lead}*{core}*{trail}'
    if s['st'] == 'bi':
        return f'{lead}***{core}***{trail}'
    return t


def page_lines(page):
    """the page's lines without the running head and the foot number, as (kind, x0, text, margin page)"""
    out = []
    for l in page['lines']:
        spans = l['spans']
        if l['top'] < 40:                                   # running head
            continue
        if l['top'] > 540 and re.fullmatch(r'\s*[\divxlc]+\s*', ''.join(s['t'] for s in spans)):
            continue                                        # page number at the foot
        margin = None
        keep = []
        for s in spans:
            m = re.fullmatch(r'\s*p\.\s*(\d+)\s*', s['t'])
            if m and s['sz'] < 9:
                margin = m.group(1)
                continue
            keep.append(s)
        if not keep:
            continue
        main = [s for s in keep if s['sz'] >= 9]
        x0 = min(s['x0'] for s in main) if main else keep[0]['x0']
        size = max(s['sz'] for s in keep)
        text = ''.join(span_text(s) if not s['sup'] else s['t'].strip().translate(SUP) for s in keep)
        text = re.sub(r'\*\*\s*\*\*', '', text)
        kind = 'h1' if size > 20 else 'h2' if size > 13 else 'h3' if size > 11.5 else 'note' if size < 10 else 'body'
        out.append([kind, x0, text, margin])
    return out


def main(src, first=FIRST_TEXT_PAGE, last=LAST_TEXT_PAGE, first_num=1):
    pages = json.load(open(src, encoding='utf-8'))
    raw = []
    for p in pages[first - 1:last]:
        raw += page_lines(p)
    # words written inside a line, with and without a hyphen (for line-end hyphens)
    inline = collections.Counter()
    for _, _, t, _ in raw:
        for w in re.findall(r"[A-Za-zāīūṭḍṇḷṃṅñ’']+(?:-[A-Za-zāīūṭḍṇḷṃṅñ’']+)+", t[:-1]):
            inline[w.lower()] += 1
            inline[w.lower().replace('-', '')] += 0
        for w in re.findall(r"[A-Za-zāīūṭḍṇḷṃṅñ’']+", t[:-1]):
            inline['=' + w.lower()] += 1

    blocks = []
    para = None

    def flush():
        nonlocal para
        if para:
            blocks.append(para)
        para = None

    def append(text):
        """add a line to the open paragraph, joining a line-end hyphen"""
        cur = para['text']
        if cur.endswith('-') and not cur.endswith(' -'):
            a = re.search(r"([A-Za-zāīūṭḍṇḷṃṅñ’'*-]+)-$", cur)
            b = re.match(r"([A-Za-zāīūṭḍṇḷṃṅñ’'*]+)", text)
            if a and b:
                left, right = a.group(1).strip('*').split('-')[-1], b.group(1).strip('*')
                joined = (left + right).lower()
                hy = (left + '-' + right).lower()
                if right[:1].isupper() or '-' in a.group(1)[:-1] or inline[hy] > inline['=' + joined]:
                    para['text'] = cur + text
                else:
                    para['text'] = cur[:-1] + text
                return
            para['text'] = cur + text
            return
        para['text'] = cur + ' ' + text

    last_h = None
    expect = first_num
    for kind, x0, text, margin in raw:
        if margin:
            if '|' in text:
                text = text.replace(' | ', f' ⟨pg:{margin}⟩ ', 1).replace('|', f'⟨pg:{margin}⟩', 1)
            else:
                text = re.sub(r'^(\d+\.\s+)?', lambda mm: (mm.group(0) or '') + f'⟨pg:{margin}⟩', text, count=1)
        text = re.sub(r'\[\*\*(\d+)\*\*\]', r'⟨pg:P\1⟩', text)
        text = text.strip()
        if kind.startswith('h'):
            text = text.replace('**', '')
            flush()
            lvl = int(kind[1])
            if last_h is not None and blocks and blocks[-1] is last_h and last_h['lvl'] == lvl:
                last_h['text'] += ' ' + text                    # a heading over two lines
                continue
            last_h = dict(type='h', text=text, lvl=lvl)
            blocks.append(last_h)
            continue
        if kind == 'note':
            if para and para.get('note_line'):
                append(text)
                continue
            flush()
            para = dict(type='p', text=text, ind=1, note_line=True)
            continue
        m = re.match(r'(\d+)\.\s+(?=\S)', text)
        numbered = bool(m) and x0 < 60 and int(m.group(1)) == expect
        if para is None or para.get('note_line') or x0 > 65 or numbered:
            flush()
            para = dict(type='p', text=text)
            if numbered:
                para['pnum'] = int(m.group(1))
                para['text'] = text[m.end():]
                expect = para['pnum'] + 1
        else:
            append(text)
    flush()
    return blocks


def parts(blocks):
    """chapters along the parts of the Pāli reader"""
    pali = json.load(open(os.path.join(ROOT, 'data', 'pali.json'), encoding='utf-8'))
    starts = {}
    for c in pali['chapters']:
        ns = [b['pnum'] for b in c['blocks'] if b.get('pnum') is not None]
        if ns:
            starts[min(ns)] = c
    chapters = []
    pending = []
    cur = None
    h1 = h2 = ''
    for b in blocks:
        if b['type'] == 'h':
            if b.get('lvl') == 1:
                h1, h2 = re.sub(r'^\d+\.\s*', '', b['text']), ''
            elif b.get('lvl') == 2 and not b['text'].startswith(('(Here Ends', 'Analysis of')):
                h2 = re.sub(r'^\d+\.\s*', '', b['text'])
            pending.append(b)
            continue
        n = b.get('pnum')
        if n is not None and n in starts and (cur is None or cur['_start'] != n):
            c = starts[n]
            rng = re.search(r'\(§[^)]*\)$', c['title'])
            split = len([x for x in pali['chapters'] if x['label'] == c['label']]) > 1
            title = (h2 if split and h2 else h1) + (' ' + rng.group(0) if rng else '')
            cur = dict(num=c['num'], label=h1 or c['label'], title=title, blocks=[], _start=n)
            chapters.append(cur)
        if cur is None:
            cur = dict(num='0', label='Front', title='Front matter', blocks=[], _start=0)
            chapters.append(cur)
        cur['blocks'] += pending + [b]
        pending = []
    if cur is not None:
        cur['blocks'] += pending
    for c in chapters:
        c.pop('_start')
        for b in c['blocks']:
            b.pop('note_line', None)
            if b['type'] == 'h':
                b.pop('lvl', None)
    return chapters


if __name__ == '__main__':
    args = sys.argv[1:]
    blocks = main(args[0], *(int(a) for a in args[1:3]))
    chapters = parts(blocks)
    out = os.path.join(ROOT, 'data', 'thittila.json')
    json.dump(dict(chapters=chapters, glossary=[]), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ps = [b['pnum'] for c in chapters for b in c['blocks'] if b.get('pnum') is not None]
    gaps = [(a, b) for a, b in zip(ps, ps[1:]) if b != a + 1]
    print(f'wrote {out}: {len(chapters)} parts, {len(ps)} numbered paragraphs, §{ps[0] if ps else "-"}–{ps[-1] if ps else "-"}; '
          f'out of order: {gaps[:15]}', file=sys.stderr)
