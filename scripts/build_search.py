#!/usr/bin/env python3
"""Render search/: the search page of the whole library and the term list it uses.

search/index.html   one search box for all the books, the results grouped by book
search/terms.json   the Pāli words and the English the books use for them, so that a search
                    for phassa also finds "contact" once a translation is in the library

The term list:
  1. CORE below: the main words of the Abhidhamma with the English of the translators
     (taken over from the Dhammasaṅgaṇī Library; a rendering is used only once it occurs in a book here).
An English rendering is kept only if it occurs somewhere in the books, so the list never
widens a search with words the library does not use. A rendering marked ~ is too common to
start a search from (searching "form" should not turn into a search for rūpa); it is still
added when the search is for the Pāli word.

The page reads each book's own search.json (written by scripts/lib/split.py), so after a book
is rebuilt there is nothing to do here unless the term list should change.

    python3 scripts/build_search.py
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = lambda s: html.escape(s, quote=False)
lib = json.load(open(os.path.join(ROOT, 'data', 'library.json'), encoding='utf-8'))

# the shelves and their order come from the home page
_spec = open(os.path.join(ROOT, 'scripts', 'build_home.py'), encoding='utf-8').read()
SHELVES = eval(re.search(r'^SHELVES = (\[.*?^\])', _spec, re.S | re.M).group(1))
SHELF_SHORT = ['Pāli', 'Commentaries']

CORE = {
    # the mind and its factors
    'phassa': 'contact; impression',
    'vedanā': 'feeling; sensation',
    'saññā': 'perception; idea',
    'cetanā': 'volition; intention',
    'citta': 'thought; consciousness; mind',
    'viññāṇa': 'consciousness; cognition',
    'mano': 'mind; ~mental',
    'vitakka': 'initial application; applied thinking; applied thought; conception',
    'vicāra': 'sustained application; sustained thought; discursive thought; investigation',
    'pīti': 'zest; rapture; joy; delightful satisfaction',
    'sukha': 'happiness; bliss; pleasure; ~ease; pleasant',
    'dukkha': 'pain; suffering; misery; painful',
    'somanassa': 'pleasure; joy; gladness; mental pleasure',
    'domanassa': 'displeasure; grief; mental pain; distress',
    'upekkhā': 'equanimity; indifference; neutral feeling; disinterestedness',
    'ekaggatā': 'one-pointedness; self-collectedness',
    'cittassekaggatā': 'one-pointedness of mind; one-pointedness of thought; self-collectedness',
    'samādhi': 'concentration; self-collectedness',
    'vīriya': 'energy; effort',
    'sati': 'mindfulness',
    'paññā': 'wisdom; understanding; insight',
    'saddhā': 'faith; confidence',
    'hiri': 'moral shame; shame; conscientiousness; modesty',
    'ottappa': 'moral dread; fear of blame; discretion',
    'ahirika': 'shamelessness; lack of moral shame; unconscientiousness',
    'anottappa': 'recklessness; lack of moral dread; indiscretion',
    'manasikāra': 'attention',
    'adhimokkha': 'decision; resolve; determination',
    'chanda': 'desire-to-do; desire to act; conation',
    'jīvitindriya': 'vitality; faculty of vitality; life-faculty; psychic life',
    'passaddhi': 'serenity; tranquillity; repose',
    'lahutā': 'lightness; buoyancy; quickness',
    'mudutā': 'malleability; plasticity; pliancy',
    'kammaññatā': 'wieldiness; workableness; adaptability; preparedness',
    'pāguññatā': 'proficiency; fitness',
    'ujukatā': 'rectitude; uprightness; straightness',
    'mettā': 'goodwill; loving-kindness; amity; love',
    'karuṇā': 'compassion; pity',
    'muditā': 'sympathetic joy; appreciative joy; sympathy',
    'appamaññā': 'illimitable; illimitables; boundless states; immeasurables',
    # the roots and the defilements
    'lobha': 'greed; lust; covetousness',
    'dosa': 'hate; hatred; aversion; anger',
    'moha': 'delusion; dullness; bewilderment',
    'alobha': 'absence of greed; non-greed; disinterestedness',
    'adosa': 'absence of hate; absence of hatred; non-hate; amity',
    'amoha': 'absence of delusion; absence of bewilderment; non-delusion; absence of dullness',
    'avijjā': 'ignorance; nescience',
    'taṇhā': 'craving',
    'diṭṭhi': 'wrong view; ~view; opinion; speculative opinion',
    'micchādiṭṭhi': 'wrong view; false view; false opinion',
    'sammādiṭṭhi': 'right view',
    'māna': 'conceit; pride',
    'vicikicchā': 'doubt; perplexity; uncertainty',
    'uddhacca': 'restlessness; distraction; excitement; flurry',
    'kukkucca': 'worry; remorse; scruple',
    'thīna': 'sloth',
    'middha': 'torpor',
    'issā': 'envy',
    'macchariya': 'avarice; stinginess; meanness',
    'abhijjhā': 'covetousness',
    'byāpāda': 'ill will; ill-will; malice',
    'paṭigha': 'aversion; repugnance; resentment; sensory reaction',
    'āsava': 'canker; taint; intoxicant',
    'saṃyojana': 'fetter',
    'gantha': 'knot; tie',
    'ogha': 'flood',
    'yoga': 'yoke',
    'nīvaraṇa': 'hindrance',
    'parāmāsa': 'contagion; misapprehension; perversion; wrong grasp',
    'upādāna': 'clinging; grasping',
    'kilesa': 'corruption; defilement; vice',
    # the kinds of states
    'kusala': '~good; wholesome; meritorious; ~moral; skilful',
    'akusala': '~bad; unwholesome; demeritorious; immoral',
    'abyākata': 'indeterminate; undetermined; neither meritorious nor demeritorious; unmoral',
    'vipāka': 'resultant; ~result; effect',
    'kiriyā': 'functional; inoperative; non-causative',
    'lokiya': 'mundane',
    'lokuttara': 'supramundane; transcendental',
    'kāmāvacara': 'sensuous sphere; sensuous plane; sense sphere; world of sense',
    'rūpāvacara': 'fine material sphere; fine-material sphere; realm of form; world of form',
    'arūpāvacara': 'non-material sphere; immaterial sphere; formless; world of the formless',
    'cetasika': 'mental factor; mental factors; mental concomitant; mental concomitants; mental property; mental properties',
    'ārammaṇa': '~object; object of thought; sense-object',
    'hetu': '~root; ~cause; ~condition',
    'jhāna': 'mental absorption; absorption; rapt musing',
    'magga': '~path',
    'phala': 'fruition; ~fruit',
    'nibbāna': 'nirvana',
    'bhavaṅga': 'life-continuum; subconsciousness',
    'anattā': 'not-self; non-self; no-self',
    'anicca': 'impermanence; impermanent',
    # matter, the aggregates, the bases, the elements
    'rūpa': 'corporeality; material form; ~matter; ~form; materiality; material properties',
    'nāma': 'mentality; ~name',
    'khandha': 'aggregate; aggregates; ~group; ~mass',
    'āyatana': '~base; ~sphere; sense-sphere; sense-base; sense-field',
    'dhātu': 'element',
    'sacca': 'truth',
    'indriya': 'faculty; controlling faculty; controlling power',
    'mahābhūta': 'great element; great elements; great essential; great primary; primary element',
    'upādārūpa': 'derived corporeality; derived matter; derivative corporeality; dependent corporeality',
    'āhāra': 'nutriment; ~food; sustenance',
    'paṭhavī': 'earth; extension',
    'āpo': 'water; cohesion; fluidity',
    'tejo': 'fire; heat',
    'vāyo': 'air; motion; wind',
    'ākāsa': 'space',
    'cakkhu': 'eye',
    'sota': 'ear',
    'ghāna': 'nose',
    'jivhā': 'tongue',
    'kāya': '~body',
    'sadda': 'sound',
    'gandha': 'odour; smell',
    'rasa': 'taste; sapid',
    'phoṭṭhabba': 'tangible; object of touch; ~touch',
}

# words too common to start a search from, wherever they come from
GENERIC = set('''will form matter object life ease group name result action base good bad moral
sphere way mass condition cause meditation wish desire fitness touch body food path root fruit view
mental thing things state states one time being mind dhamma dhammas'''.split())

MAP = str.maketrans({'ā': 'a', 'ī': 'i', 'ū': 'u', 'ṃ': 'm', 'ṁ': 'm', 'ṅ': 'n', 'ñ': 'n', 'ṭ': 't',
                     'ḍ': 'd', 'ṇ': 'n', 'ḷ': 'l', 'ṛ': 'r', 'ś': 's', 'ṣ': 's', 'ç': 's', 'ḥ': 'h',
                     'â': 'a', 'î': 'i', 'û': 'u'})


def norm(s):
    return s.lower().translate(MAP)


# ---- the corpus, for checking that a rendering occurs
books = lib['books']
shelf_of = {s: k for k, (_, _, ss) in enumerate(SHELVES) for s in ss}
books.sort(key=lambda b: (shelf_of[b['slug']], SHELVES[shelf_of[b['slug']]][2].index(b['slug'])))
corpus = ' '.join(norm(u[2]) for b in books
                  for u in json.load(open(os.path.join(ROOT, b['slug'], 'search.json'), encoding='utf-8'))['u'])


def occurs(phrase):
    return re.search(r'(?<![a-z])' + re.escape(norm(phrase)) + r's?(?![a-z])', corpus) is not None


terms = {}      # pāli (with diacritics) -> {english: trigger?}
dropped = []


def add(pali, eng, trigger=True):
    eng = eng.strip()
    if not eng:
        return
    low = eng.lower()
    if low.startswith('~'):
        low, trigger = low[1:].strip(), False
    if low in GENERIC:
        trigger = False
    if not occurs(low):
        dropped.append((pali, low))
        return
    d = terms.setdefault(pali, {})
    d[low] = d.get(low, False) or trigger


for p, rs in CORE.items():
    for r in rs.split(';'):
        add(p, r)

n_khine = 0

out = []
for p in sorted(terms):
    rs = terms[p]
    out.append([p, [[r, 1 if t else 0] for r, t in rs.items()]])
os.makedirs(os.path.join(ROOT, 'search'), exist_ok=True)
json.dump({'note': 'Pāli words and the English the books of the library use for them; written by scripts/build_search.py. [pāli, [[english, 1 = a search for the English also searches the Pāli]]]',
           't': out}, open(os.path.join(ROOT, 'search', 'terms.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))

# ---- the page
meta = []
for b in books:
    k = shelf_of[b['slug']]
    meta.append({'slug': b['slug'], 'cite': b.get('cite', b['author']), 'title': b['title'], 'shelf': k})
shelves = [{'name': SHELVES[k][0], 'short': SHELF_SHORT[k]} for k in range(len(SHELVES))]

tpl = open(os.path.join(ROOT, 'scripts', 'search.html'), encoding='utf-8').read()
page = (tpl.replace('{{TITLE}}', e(lib['title']))
           .replace('{{NBOOKS}}', str(len(books)))
           .replace('{{DATA}}', json.dumps({'books': meta, 'shelves': shelves}, ensure_ascii=False).replace('</', '<\\/')))
open(os.path.join(ROOT, 'search', 'index.html'), 'w', encoding='utf-8').write(page)
print(f'wrote search/terms.json: {len(out)} Pāli words, {sum(len(r) for _, r in out)} renderings '
      f'; {len(dropped)} renderings dropped as not in the books')
print(f'wrote search/index.html: {len(page)} bytes')
if os.environ.get('VERBOSE'):
    for p, r in dropped:
        print('  dropped', p, '→', r)
