# Autopilot log

Newest first. See AUTOPILOT.md for the rules.

## 2026-11-26 08:04 UTC — text to §354 (Paṭiccasamuppādavibhaṅga)

- §225–354, two new parts (ch8 Suttanta, ch9 Abhidhamma), PDF pp. 279–352; no paragraphs out of order. §1–224 unchanged (diff is additions only).
- Parser: after a closing "(Here Ends) …" heading, the next heading line starts a new heading unless it is the closing line's own wrap (gap under 20 pt). This splits "(Here Ends) Reciprocity Tetrad" / "Summary" and the two closing lines at the end of the Abhidhamma section; "… Rooted in / Ignorance" stays one line. The `raw` lines now carry their top.
- data/structure.json: vibhaṅga 6 added (18 headings; "Summary" pairs with Pāli "Mātikā"). Doubtful: the 7th Association Tetrad starts at Thiṭṭila §264, Pāli heading at §265.
- As in earlier parts, a part's first block is the closing line of the part before ("(Here Ends) Analysis According to the Discourses"); left as it is so earlier output stays the same.
- No Interrogation section in this vibhaṅga, so no tags. Spot-checked §230, §281 against the Pāli. check_site 0 problems, check_phone 0 failures.

## 2026-11-26 07:30 UTC — text to §224 (Āyatana-, Dhātu-, Sacca-, Indriyavibhaṅga)

- §154–224, four new parts (ch4–ch7), PDF pp. 91–278; no paragraphs out of order.
- Parser: (1) a numbered heading no longer merges into the 12 pt closing line before it ("This is Called … 2. The Aggregate of Feeling" is now two headings; this splits four such headings in the Khandhavibhaṅga's Abhidhamma section, §1–153 paragraphs unchanged); (2) at a new vibhaṅga, the closing lines of the last one ("(Here Ends the Section) Interrogation", "… is Ended") stay with it; (3) `lvl` is kept on headings, as AUTOPILOT.md asks (added to the earlier parts too).
- New `scripts/thittila/structure.py` writes `data/structure.json` (vibhaṅgas 1–5, 43 headings, Pāli and English paired, § ranges). Run it after each text chunk.
- Doubtful: Thiṭṭila numbers §185 (the Dhātu Interrogation's opening list), which the Pāli leaves unnumbered. Interrogation paragraphs not tagged: each Tika/Duka answer is one paragraph covering all the triplets/couplets, so no single mātikā tag fits.
- Spot-checked §166, §203 against the Pāli. check_site 0 problems, check_phone 0 failures.

## 2026-11-26 — set up

Thiṭṭila §1–153 done by hand (parser in scripts/thittila/). Queue: six text chunks (§154–1044), the front matter, the index.
