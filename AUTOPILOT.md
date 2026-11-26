# Autopilot: finishing Thiṭṭila's Book of Analysis, then translating the commentaries

A scheduled task runs every hour. Each run is a fresh session with no memory. All it knows is this
file, `data/autopilot.json` (the queue) and `AUTOPILOT_LOG.md` (what earlier runs did). The owner
asked on 2026-11-26 for the work to go **in small chunks**, so that the token budget lasts. Do one
chunk per run, then stop.

## Setup at the start of every run

1. Attach and clone the repo: `add_repo etomelk/vibhanga-library` (push), then clone it to
   `/home/claude/vibhanga-library`. Commit as Claude (`git config user.name Claude; git config user.email
   noreply@anthropic.com`), and end each commit message with `Co-Authored-By: Claude <noreply@anthropic.com>`.
2. Read `data/autopilot.json`. If `status` is `done`, `paused` or `blocked`, stop with no changes. If
   `lock` holds a time less than 2 hours old, stop. Otherwise set `lock` to the current UTC time,
   commit and push it, and clear it at the end of the run.
3. The source PDF is in the repo: `sources/thittila.pdf`. It is the PTS electronic edition (CC BY-NC
   3.0), 699 pages; it is kept out of the published site by `netlify.toml`.
   Then `pip install pdfplumber --break-system-packages` if it is missing, and run
   `python3 scripts/thittila/extract.py sources/thittila.pdf work/lines.json`.

## One run = one chunk

Take the first item of `queue` in `data/autopilot.json`:

- **`text` items** (`to_page`, `to_para`): run `python3 scripts/thittila/parse.py work/lines.json 91 <to_page>`.
  It must report numbered paragraphs §1–`to_para` with **no paragraphs out of order**. Where some are out
  of order, look at those pages in `work/lines.json` and fix the parser, never the data. Typical causes
  are a numbered list inside a paragraph, a table, or a range ("45–47."). The fix must not change the
  earlier output: after the fix, the paragraphs already done must come out the same. Check this with
  `git diff --stat data/thittila.json` and a look at the diff.
- **`front` item**: add the front matter (PDF pages 1–90: the editorial note, the biography, the
  translator's preface and the Introduction) as a part `0` before the text. Its headings are 24.8 pt.
- **`index` item**: the Index of Terms and Phrases Defined (PDF pages 679–696) becomes the book's
  `glossary` (its entries link to pages; see how the Dhammasaṅgaṇī Library's `scripts/rhysdavids/parse.py`
  does Rhys Davids' index), and the Bibliography (697–699) becomes a last part.

- **`translate` items** (`book`: `sammoha`, then `mulatika`, then `anutika`): see "Translating" below.

Update the book's `note` in `data/library.json` so that it says how far the text goes.

## Checks before every push

`python3 scripts/build.py thittila`, `python3 scripts/build_home.py`, `python3 scripts/build_search.py`
and `python3 scripts/build_compare.py`. Then `python3 scripts/check_site.py` must report **0 problems**, and
`python3 scripts/check_phone.py thittila` must report **0 failures**. Every other book must stay
byte-identical: `git status` shows only thittila/, data/thittila.json, data/library.json, the home,
search and compare pages, and this autopilot's files. Spot-check two paragraphs of the new chunk against
the Pāli (same §, same content).

Then remove the item from `queue` (a `translate` item stays until its whole book is done), clear `lock`, add an entry at the top of `AUTOPILOT_LOG.md` (the
date, the item, paragraphs and parts produced, parser changes, anything doubtful), commit and push to
`main`. If the checks cannot be made to pass within the run, push nothing but the log entry and the
lock cleared. Leave the item in the queue with a `note`, and after the same item has failed twice, set
`status` to `blocked`.

## Translating (the `translate` items)

The owner asked on 2026-11-26 for the commentaries to be translated into English, in this order: the
Sammohavinodanī first, then the Mūlaṭīkā (which explains it), then the Anuṭīkā (which explains the
Mūlaṭīkā). The same was done for the Dhammasaṅgaṇī's sub-commentaries in etomelk/dhammasangani-library,
and its conventions and term list are copied into `data/translations/README.md`. **Read that README
first, every run.**

- **One chunk** is about **2,500 Pāli words**. Take the rest of the part if that is no more than ~3,000
  words; otherwise take blocks up to ~2,500 words, ending at a block boundary (a heading, or the end of
  an argument, is best). The position is `next` in `data/autopilot.json`: `{"book", "part", "block"}`.
  Print the Pāli with `python3 scripts/translation/show.py <book> <part> <from>`.
- **Accuracy first.** Translate what the Pāli says, literally, following its argument and grammar.
  Never paraphrase loosely, summarise, skip a sentence or add explanation that is not in the text. Where
  a reading or a sense is uncertain, give the best rendering and mark it `[?: why]`; list every `[?]` in
  the log.
- **One style.** Before translating, read the last part done of the same book (and, for a book's first
  part, part 1 of the book before it) to keep the voice the same. A new technical term gets a fixed
  rendering in the README's term list, in the same commit, and keeps it from then on.
- **Files.** Write `data/translations/<book>/<NN>.md` (NN = the part, two digits). Create it with the
  `label:` / `title:` header if it is new (the label in English, e.g. "Analysis of the Aggregates", as
  Thiṭṭila names the vibhaṅga; the title "English (Pāli title)"). Then append `@<block>` entries in
  order: every block gets an entry, headings and verse lines included.
- **Build and check:** `python3 scripts/build_translation.py` must print no `!` problems (every block
  present, every `⟨pg:…⟩` marker kept). Then run the checks above with `<book>-en` in place of thittila
  (check_phone on `<book>-en`), and look once at the new part beside the Pāli
  (`compare/?a=<book>&b=<book>-en`). A partly translated part shows its remaining blocks in Pāli,
  marked "not yet translated"; that is expected between runs.
- **Then** set `next` to the block after the chunk (at the end of a part, block 0 of the next part; at
  the end of a book, remove its item from `queue` and set `next` to part 0, block 0 of the next book).
  Log the book, part, blocks, Pāli words, every `[?]` and any new term.
- **The end.** When the queue is empty, one last run reads the three books through for consistency
  (the term list applied everywhere, the lemma format, the headings), gathers the `[?]` list into the
  last log entry, and sets `status` to `done`.

## For the owner

- To pause, set `"status": "paused"` in `data/autopilot.json` (or ask Claude to). To resume, set it to
  `"running"`.
- Progress is in `AUTOPILOT_LOG.md`, and on the site: the draft translations shelf shows each book from
  its first part on, with how much is done.
