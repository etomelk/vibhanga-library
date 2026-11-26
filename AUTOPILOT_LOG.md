# Autopilot log

Newest first. See AUTOPILOT.md for the rules.

## 2026-11-26 07:30 UTC — text to §224 (Āyatana-, Dhātu-, Sacca-, Indriyavibhaṅga)

- §154–224, four new parts (ch4–ch7), PDF pp. 91–278; no paragraphs out of order.
- Parser: (1) a numbered heading no longer merges into the 12 pt closing line before it ("This is Called … 2. The Aggregate of Feeling" is now two headings; this splits four such headings in the Khandhavibhaṅga's Abhidhamma section, §1–153 paragraphs unchanged); (2) at a new vibhaṅga, the closing lines of the last one ("(Here Ends the Section) Interrogation", "… is Ended") stay with it; (3) `lvl` is kept on headings, as AUTOPILOT.md asks (added to the earlier parts too).
- New `scripts/thittila/structure.py` writes `data/structure.json` (vibhaṅgas 1–5, 43 headings, Pāli and English paired, § ranges). Run it after each text chunk.
- Doubtful: Thiṭṭila numbers §185 (the Dhātu Interrogation's opening list), which the Pāli leaves unnumbered. Interrogation paragraphs not tagged: each Tika/Duka answer is one paragraph covering all the triplets/couplets, so no single mātikā tag fits.
- Spot-checked §166, §203 against the Pāli. check_site 0 problems, check_phone 0 failures.

## 2026-11-26 — set up

Thiṭṭila §1–153 done by hand (parser in scripts/thittila/). Queue: six text chunks (§154–1044), the front matter, the index.
