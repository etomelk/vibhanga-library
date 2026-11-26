#!/usr/bin/env python3
"""Look up Pāli words of the two ṭīkās in the Digital Pāḷi Dictionary (DPD, Bodhirasa Bhikkhu,
dpdict.net, CC BY-NC-SA 4.0); the subset in dpd-tika.sqlite.gz holds the forms that occur in the
Mūlaṭīkā and the Anuṭīkā (made by build_dpd.py from github.com/digitalpalidictionary/dpd-db).
   python3 scripts/translation/dpd.py word [word ...]
Inflected forms are found; a word with -ti/-nti (iti) is split; a compound not in the dictionary
is split at the longest known first member (check such splits yourself)."""
import gzip, os, shutil, sqlite3, sys
HERE = os.path.dirname(os.path.abspath(__file__))
DB = '/tmp/dpd-tika.sqlite'
if not os.path.exists(DB):
    with gzip.open(os.path.join(HERE, 'dpd-tika.sqlite.gz'), 'rb') as f, open(DB, 'wb') as g:
        shutil.copyfileobj(f, g)
c = sqlite3.connect(DB).cursor()
def hits(w):
    return c.execute('select distinct hw.lemma,hw.pos,hw.meaning,hw.construction from inf join hw on hw.id=inf.id '
                     'where inf.form=? order by length(hw.meaning)>0 desc limit 6', (w,)).fetchall()
def stems(w):
    return c.execute("select lemma,pos,meaning,construction from hw where (lemma=? or lemma like ?) and meaning!='' limit 4",
                     (w, w + ' %')).fetchall()
def look(w, depth=0):
    w = w.lower().strip('‘’“”,.;:?!()[]*')
    h = hits(w)
    if h:
        return [(w, h)]
    for suf, rep in (('nti', 'ṃ'), ('nti', ''), ('ti', ''), ('ti', 'ā'), ('ti', 'a')):
        if w.endswith(suf) and len(w) > len(suf) + 2:
            h = hits(w[:-len(suf)] + rep)
            if h:
                return [(w[:-len(suf)] + rep, h), ('iti', [('iti', 'ind', 'thus; (quotation marker)', '')])]
    if depth < 2:
        for i in range(len(w) - 3, 2, -1):
            a, b = w[:i], w[i:]
            for a2 in (a, a + 'a'):
                h = hits(a2) or stems(a2)
                if h:
                    rest = look(b, depth + 1)
                    if rest:
                        return [(a2, h)] + rest
    return []
for w in sys.argv[1:]:
    r = look(w)
    print(f'== {w}')
    if not r:
        print('   (not found)')
    for part, hs in r:
        for lem, pos, m, con in hs[:3]:
            print(f'   {part:18} {lem} ({pos}) {m}' + (f'  [{con}]' if con else ''))
