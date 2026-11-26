# Vibhaṅga Library

Study editions of the Vibhaṅga, the second book of the Abhidhamma Piṭaka. The site holds the text
and its commentaries. It is a static website: a home page that lists the books, one reader per book
(all sharing the same template, stylesheet and script), a search of all the books, a side-by-side view
and a reference list.

The reader, the build scripts and the checks were copied from the Dhammasaṅgaṇī Library
(etomelk/dhammasangani-library) and adapted. Nothing here is linked to that site, and nothing here
changes it.

**Status: begun** (November 2026). The four Pāli texts of the Sixth Council edition are in. Translations
and study notes are to come.

## The books

| Shelf | Folder | Book | Source of the text |
|---|---|---|---|
| 1. The Vibhaṅga in Pāli | `pali/` | Vibhaṅgapāḷi, Sixth Council edition | VRI tipitaka-xml `romn/abh02m.mul.xml` |
| 2. The commentaries | `sammoha/` | Sammohavinodanī (Vibhaṅga-aṭṭhakathā) | `romn/abh02a.att.xml` |
| | `mulatika/` | Vibhaṅga-mūlaṭīkā | `romn/abh02t.tik.xml`, its first book |
| | `anutika/` | Vibhaṅga-anuṭīkā | `romn/abh02t.tik.xml`, its second book |

The VRI files are at github.com/VipassanaTech/tipitaka-xml. The shelves and their order are set in
`scripts/build_home.py` (SHELVES). The books' reader settings are in `data/library.json`.

```
index.html              library home: the shelves, About this library, A note on rights
<slug>/                 one split reader per book: index.html + c/<part>.html, ids.json, search.json
search/                 search of all the books at once (scripts/build_search.py; shared/search.js)
compare/                two books side by side, kept in step (scripts/build_compare.py; shared/compare.js)
references/index.html   the reference list (data/references.json, written by scripts/make_references.py)
shared/                 reader.css, reader.js, home.css, search.js, compare.js/.css, words.js
data/library.json       the books and their reader settings
data/<slug>.json        the structured text of each book
data/vibhanga-pts.json  Sixth Council § -> PTS §; identity for now; the books that share it link § to §
scripts/pali/convert.py the four Pāli texts from the VRI files
scripts/build.py        renders one book:  python3 scripts/build.py <slug>
scripts/check_site.py   loads every page at 320, 400 and 1300 px: horizontal overflow, console errors, failed requests
scripts/check_phone.py  phone emulation: taps on the sidebar sections and "In this part" in every part of a book
```

Rebuilding everything:

```sh
R=path/to/tipitaka-xml/romn
python3 scripts/pali/convert.py $R/abh02m.mul.xml pali
python3 scripts/pali/convert.py $R/abh02a.att.xml sammoha
python3 scripts/pali/convert.py $R/abh02t.tik.xml mulatika "Vibhaṅga-mūlaṭīkā"
python3 scripts/pali/convert.py $R/abh02t.tik.xml anutika "Vibhaṅga-anuṭīkā"
for s in pali sammoha mulatika anutika; do python3 scripts/build.py $s; done
python3 scripts/make_references.py && python3 scripts/build_home.py
python3 scripts/build_search.py && python3 scripts/build_compare.py
python3 scripts/check_site.py
```

## The Pāli texts

- **Numbers.** The Vibhaṅga's paragraphs are numbered §1–1044, as in the Sixth Council edition. VRI numbers
  a commentary's paragraphs by the Vibhaṅga paragraph they explain. So all four books share one numbering,
  and each § carries chips to the same paragraph in the others. A commentary paragraph that covers a range
  ("196-7", "248-249") keeps the whole range.
- **Pages.** The pages of the Myanmar edition (`pb ed="M"`) are page anchors (#pg12). The pages of the PTS
  editions (`pb ed="P"`) are page anchors marked P (#pgP12). For the Vibhaṅga that edition is Rhys Davids
  1904, whose pages U Thiṭṭila's *Book of Analysis* gives. For the Sammohavinodanī it is Buddhadatta 1923,
  whose pages Ñāṇamoli's *Dispeller of Delusion* gives. The Thai (T) and VRI (V) page numbers of the file
  are left out.
- **Parts.** There is one part per vibhaṅga. A vibhaṅga of more than 9,000 words is cut at its titles (the
  bhājanīyas, the niddesas), and a title section of more than 9,000 words is cut at its subheads, into parts
  of about 6,000 words (`SPLIT`, `TARGET` in the script).
- **The text is unchanged.** Bold (in the commentaries, the words explained), verses and the variant readings (in the
  Vibhaṅga, as notes) are kept.

## Adding a book

1. Produce `data/<slug>.json`. The block types are those of the Dhammasaṅgaṇī Library (see
   `scripts/build.py`). A scanned book goes through that library's scan pipeline (`scripts/muller/` there).
2. Add the book to `data/library.json`, and to a shelf in `scripts/build_home.py` at its place in the
   reading order, from the most approachable to the most demanding. A book numbered by the Sixth Council §
   gets `"pts_map": "vibhanga-pts.json"` and links to the others at once. A book numbered by the PTS
   sections gets `"pts_sections": true`, once `data/vibhanga-pts.json` holds the real PTS numbers.
3. `python3 scripts/build.py <slug>`, `python3 scripts/build_home.py`, `python3 scripts/build_search.py`,
   `python3 scripts/build_compare.py`, then `scripts/check_site.py` and `scripts/check_phone.py <slug>`.
