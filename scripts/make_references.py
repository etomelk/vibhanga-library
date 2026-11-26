#!/usr/bin/env python3
"""Write data/references.json: the reference list of the Vibhaṅga Library, grouped
by area. The list is the library's own (there is no source list, so no entry is marked
added): every work was checked against a library catalogue, the publisher or the scan
itself. The work that is a book in this library links to its reader (lib=)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

AREAS = [
    ('editions', 'Editions of the text', 'Pāli editions of the Vibhaṅga and of its commentary, the Sammohavinodanī, with its sub-commentaries.'),
    ('translations', 'Translations', 'The Vibhaṅga and the Sammohavinodanī in English.'),
    ('reference', 'Reference works', 'Dictionaries, handbooks and the online Tipiṭaka sites and readers used alongside the text.'),
]

R = []
def add(area, authors, year, title, where='', url='', lib='', found='', label='', added=False):
    """url: a link given in a source list (this library has none, so it stays empty).
    found: a link located and opened for this library — a public-domain scan (Scan), an
    open-access article (Article), a lending-library copy (Borrow), the publisher's or
    author's own page (Publisher), or a free online resource published by its makers
    (Online); label says which. lib: the slug of a book in this library (Read here)."""
    d = dict(area=area, authors=authors, year=year, title=title, where=where, url=url, lib=lib, found=found, label=label)
    if added:
        d['added'] = True       # not used here: the list has no source list to be added to
    R.append(d)

# --- Editions of the text
add('editions', 'Rhys Davids, C. A. F. (Ed.)', '1904', 'The Vibhaṅga, being the second book of the Abhidhamma Piṭaka', 'London: Pali Text Society (Henry Frowde) (reprinted 1978)', found='https://openlibrary.org/borrow/ia/vibhagabeingsec00davigoog', label='Scan')
add('editions', 'Buddhadatta, A. P. (Ed.)', '1923', 'Sammohavinodanī: Abhidhamma-piṭake Vibhaṅgaṭṭhakathā', 'London: Pali Text Society (reprinted 1980)', found='https://palitextsociety.org/?p=5289', label='Publisher')
add('editions', 'Chaṭṭha Saṅgāyana', '1956', 'Abhidhammapiṭaka, Vibhaṅgapāḷi (Sixth Council edition)', 'Yangon: Buddhasāsana Samiti; digital edition, Vipassana Research Institute (romn/abh02m.mul.xml)', lib='pali/', found='https://tipitaka.org/', label='Online')
add('editions', 'Chaṭṭha Saṅgāyana', '1956b', 'Vibhaṅga-aṭṭhakathā (Sammohavinodanī), -mūlaṭīkā and -anuṭīkā (Sixth Council edition)', 'Yangon: Buddhasāsana Samiti; digital edition, Vipassana Research Institute (romn/abh02a.att.xml, abh02t.tik.xml)', lib='sammoha/', found='https://tipitaka.org/', label='Online')

# --- Translations
add('translations', 'Thiṭṭila, P. A. (Trans.)', '1969', 'The book of analysis (Vibhaṅga): The second book of the Abhidhamma Piṭaka, translated from the Pāḷi of the Burmese Chaṭṭhasaṅgīti edition', 'London: Pali Text Society (Luzac) (Translation Series 39; reprinted 1988, 1995, 2010)', found='https://palitextsociety.org/?p=818', label='Publisher')
add('translations', 'Ñāṇamoli (Trans.); Cousins, L. S., Nyanaponika, & Shaw, C. M. M. (Rev.)', '1987–1991', 'The dispeller of delusion (Sammohavinodanī) (Parts I–II)', 'London: Pali Text Society (Sacred Books of the Buddhists 40–41; reprinted as one volume 2017)', found='https://palitextsociety.org/?p=4932', label='Publisher')

# --- Reference works
add('reference', 'Bodhirasa', 'n.d.', 'Digital Pāḷi dictionary [online dictionary]', '', found='https://dpdict.net', label='Online')
add('reference', 'Cone, M.', '2001–2020', 'A dictionary of Pāli (Vols. I–III)', 'The Pali Text Society (searchable online through the Society)', found='https://palitextsociety.org/a-dictionary-of-pali-online/', label='Publisher')
add('reference', 'Malalasekera, G. P.', '1937–1938', 'Dictionary of Pāli proper names (Vols. I–II)', 'London: John Murray (Indian Texts Series)')
add('reference', 'Nyanatiloka', '1980', 'Buddhist dictionary: Manual of Buddhist terms and doctrines (Nyanaponika, Ed.; 4th rev. ed.)', 'Kandy: Buddhist Publication Society (first published 1952)', found='https://bps.lk/book/buddhist-dictionary', label='Publisher')
add('reference', 'Ñāṇamoli', '1994', 'A Pali-English glossary of Buddhist technical terms (Bodhi, Ed.)', 'Kandy: Buddhist Publication Society (2nd ed. 2007)', found='https://www.bps.lk/olib/bp/bp608s_Nyanamoli_Pali-Glossary.pdf', label='Publisher')
add('reference', 'Rhys Davids, T. W., & Stede, W. (Eds.)', '1921–1925', 'The Pali Text Society’s Pali-English dictionary', 'Chipstead: The Pali Text Society (searchable edition, Digital Dictionaries of South Asia, University of Chicago)', found='https://dsal.uchicago.edu/dictionaries/pali/index.html', label='Online')
add('reference', 'Trenckner, V., Andersen, D., Smith, H., et al. (Eds.)', '1925–2011', 'A critical Pāli dictionary (Vols. I–III)', 'Copenhagen: Royal Danish Academy of Sciences and Letters (online edition, University of Cologne, with the Pali Text Society)', found='https://cpd.uni-koeln.de/', label='Online')
add('reference', 'Sirimangalo International', 'n.d.', 'Digital Pāḷi reader [the canon with its aṭṭhakathā and ṭīkā, dictionaries and search]', 'Sirimangalo.org', found='https://pali.sirimangalo.org/', label='Online')
add('reference', 'SuttaCentral', 'n.d.', 'SuttaCentral: Early Buddhist texts, translations, and parallels', 'SuttaCentral', found='https://suttacentral.net/', label='Online')
add('reference', 'Vipassana Research Institute', 'n.d.', 'The Pāḷi Tipiṭaka [Chaṭṭha Saṅgāyana edition, with the aṭṭhakathā and ṭīkā]', 'Igatpuri: Vipassana Research Institute', found='https://tipitaka.org/', label='Online')

json.dump(dict(areas=[dict(id=a, name=n, blurb=b) for a, n, b in AREAS], refs=R),
          open(os.path.join(ROOT, 'data', 'references.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(R), 'references')
