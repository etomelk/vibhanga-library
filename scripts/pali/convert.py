"""Build data/<slug>.json from a VRI file of the Vibhaṅga or its commentaries (Chaṭṭha Saṅgāyana text,
github.com/VipassanaTech/tipitaka-xml):

python3 scripts/pali/convert.py romn/abh02m.mul.xml pali                          # Vibhaṅgapāḷi
python3 scripts/pali/convert.py romn/abh02a.att.xml sammoha                       # Sammohavinodanī
python3 scripts/pali/convert.py romn/abh02t.tik.xml mulatika "Vibhaṅga-mūlaṭīkā"  # the Mūlaṭīkā
python3 scripts/pali/convert.py romn/abh02t.tik.xml anutika "Vibhaṅga-anuṭīkā"    # the Anuṭīkā

- The paragraph numbers are the Sixth Council's (§1–1044 of the Vibhaṅga); VRI numbers a commentary's
  paragraphs by the Vibhaṅga paragraph they explain, so every book shares one numbering (anchor #p<n>).
- The pages of the Myanmar edition (pb ed="M") are page anchors #pg<n>; the pages of the PTS edition
  (pb ed="P": the Vibhaṅga of 1904, the Sammohavinodanī of 1923) are #pgP<n>.
- The variant readings (<note>) are footnotes, numbered through each part; in a heading they stay in brackets.
- Parts: one per vibhaṅga (chapter); a vibhaṅga of more than SPLIT words is cut at its titles
  (the bhājanīyas, the niddesas) into parts of about TARGET words.
- The file abh02t.tik.xml holds two books (the Mūlaṭīkā, then the Anuṭīkā): the third argument picks one."""
import html
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SPLIT = 9000
TARGET = 6000


def text_of(inner, notes):
    def note(m):
        v = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).strip()
        if notes is None:
            return f'({v})'
        notes.append(v)
        return '[^%d]' % len(notes)
    t = re.sub(r'<hi rend="paranum">[\d\-–]+</hi><hi rend="dot">\.</hi>\s*', '', inner)
    t = re.sub(r'<note>(.*?)</note>', note, t)
    t = re.sub(r'<pb ed="M" n="\d+\.0*(\d+)"\s*/>', r'⟨pg:\1⟩', t)
    t = re.sub(r'<pb ed="P" n="\d+\.0*(\d+)"\s*/>', r'⟨pg:P\1⟩', t)
    t = re.sub(r'<hi rend="bold">(.*?)</hi>', r'**\1**', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = re.sub(r'\*\*\s*\*\*', ' ', t)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def words(b):
    return len(re.sub(r'⟨[^⟩]*⟩|\[\^\d+\]', '', b.get('text', '')).split()) if not b.get('note') else 0


def main(src, slug, book=None):
    raw = open(src, 'rb').read()
    try:
        x = raw.decode('utf-16')
    except UnicodeDecodeError:
        x = raw.decode('utf-8')
    body = x[x.index('<body'):]
    if book:                                    # one book of a file that holds two
        marks = [(m.start(), html.unescape(m.group(1))) for m in re.finditer(r'<p rend="book">(.*?)</p>', body)]
        i = [k for k, (_, t) in enumerate(marks) if t.strip() == book]
        assert i, f'no book {book!r} in {src}: {[t for _, t in marks]}'
        a = marks[i[0]][0]
        z = marks[i[0] + 1][0] if i[0] + 1 < len(marks) else len(body)
        body = body[a:z]
    # vibhaṅgas: [name, [sections]], a section = [title, blocks]
    vibh = []
    pre = []
    for m in re.finditer(r'<p rend="(\w+)"(?: n="([\d\-–]+)")?>(.*?)</p>', body, flags=re.S):
        rend, n, inner = m.group(1), m.group(2), m.group(3)
        if rend in ('nikaya', 'book'):
            continue
        if rend == 'chapter':
            name = text_of(inner, None)
            vibh.append([name, [['', [dict(type='h', text=name)]]]])
            continue
        if rend == 'title' and vibh:
            t = text_of(inner, None)
            vibh[-1][1].append([t, [dict(type='h', text=t)]])
            continue
        blocks = vibh[-1][1][-1][1] if vibh else pre
        if rend in ('subhead', 'subsubhead', 'title'):
            blocks.append(dict(type='h', text=text_of(inner, None)))
            continue
        notes = []
        t = text_of(inner, notes)
        if rend == 'centre':
            b = dict(type='p', text=t, ctr=True)
        elif rend.startswith('gatha'):
            b = dict(type='p', text=t, ind=2)
        elif n:
            b = dict(type='p', pnum=int(re.match(r'\d+', n).group()), text=t)
            if not re.fullmatch(r'\d+', n):           # "248-249", or abbreviated "196-7" (= 196–197)
                a, z = re.split(r'[\-–]', n)
                b['pend'] = int(a[:len(a) - len(z)] + z)
        elif rend == 'indent':
            b = dict(type='p', text=t, ind=1)
        else:
            b = dict(type='p', text=t)
        b['_notes'] = notes
        blocks.append(b)
    # a title section longer than SPLIT is cut at its subheads, so that no page is too long
    for v in vibh:
        out_secs = []
        for t, bl in v[1]:
            if sum(words(b) for b in bl) <= SPLIT:
                out_secs.append([t, bl])
                continue
            cur, w = None, 0
            for b in bl:
                if cur is None or (b['type'] == 'h' and w >= TARGET):
                    cur, w = [t, []], 0
                    out_secs.append(cur)
                cur[1].append(b)
                w += words(b)
        v[1] = out_secs
    # a section that is only headings joins the next one
    for v in vibh:
        merged = []
        carry = []
        for t, bl in v[1]:
            if all(b['type'] == 'h' for b in bl):
                carry += bl
                continue
            merged.append([t, carry + bl])
            carry = []
        if carry and merged:
            merged[-1][1] += carry
        v[1] = merged
    # parts
    parts = []
    for name, secs in vibh:
        total = sum(words(b) for _, bl in secs for b in bl)
        label = re.sub(r'^\d+\.\s*', '', name)
        if total <= SPLIT:
            parts.append([label, [s for s in secs]])
            continue
        cur = None
        for s in secs:
            w = sum(words(b) for b in s[1])
            if cur is None or (cur[2] + w > TARGET and cur[2] > 0):
                cur = [label, [], 0]
                parts.append(cur)
            cur[1].append(s)
            cur[2] += w
    if pre and parts:
        parts[0][1].insert(0, ['', pre])
    chapters = []
    for i, p in enumerate(parts, 1):
        label, secs = p[0], p[1]
        blocks = []
        k = 0
        for _, bl in secs:
            for b in bl:
                ns = b.pop('_notes', [])
                if ns:
                    off = k
                    b['text'] = re.sub(r'\[\^(\d+)\]', lambda mm: f'[^{int(mm.group(1)) + off}]', b['text'])
                blocks.append(b)
                for v in ns:
                    k += 1
                    blocks.append(dict(type='p', note=k, text=v))
        nums = [b['pnum'] for b in blocks if b.get('pnum') is not None] + [b['pend'] for b in blocks if b.get('pend')]
        titles = [re.sub(r'^\(?\d+\.\)?\s*', '', t) for t, _ in secs if t]
        if len([q for q in parts if q[0] == label]) > 1 or not titles:
            title = ', '.join(titles) if titles else label
        else:
            title = label
        if nums:
            title += f' (§{min(nums)}–{max(nums)})' if min(nums) != max(nums) else f' (§{min(nums)})'
        chapters.append(dict(num=str(i), label=label, title=title, blocks=blocks))
    out = os.path.join(ROOT, 'data', f'{slug}.json')
    json.dump(dict(chapters=chapters, glossary=[]), open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ps = [b['pnum'] for c in chapters for b in c['blocks'] if b.get('pnum') is not None]
    dup = sorted({p for p in ps if ps.count(p) > 1})
    print(f'wrote {out}: {len(chapters)} parts, {len(ps)} numbered paragraphs (§{min(ps)}–{max(ps)}), '
          f'{sum(1 for c in chapters for b in c["blocks"] if b.get("note"))} notes, duplicates: {dup[:12]}', file=sys.stderr)
    for c in chapters:
        print(f'  {c["num"]:>3} {c["label"][:26]:26} {c["title"][:60]:60} {sum(words(b) for b in c["blocks"]):6}', file=sys.stderr)


if __name__ == '__main__':
    main(*sys.argv[1:4])
