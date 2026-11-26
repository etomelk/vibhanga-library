# Draft translations of the Vibhaṅga commentaries

English translations of the Sammohavinodanī, the Vibhaṅga-mūlaṭīkā and the Vibhaṅga-anuṭīkā. They
are made with Claude for this library from the Sixth Council (VRI) Pāli, paragraph by paragraph. They
are **drafts**: to be read beside the Pāli and checked by someone who reads the Abhidhamma commentaries.
Corrections go straight into these files. `python3 scripts/build_translation.py` then rebuilds the books
(`sammoha-en/`, `mulatika-en/`, `anutika-en/`), and `python3 scripts/build_compare.py` the side-by-side
alignment. The conventions and the term list were taken over from the Dhammasaṅgaṇī Library, so that
the two libraries render the same Pāli the same way.

## Files

`sammoha/NN.md`, `mulatika/NN.md` and `anutika/NN.md` hold part NN of `data/<book>.json`. A header gives
the part's English label and title. Then comes one entry per block of the Pāli part, `@0`, `@1`, … in
order, with every block present (headings, verse lines and the closing "… niṭṭhitā" lines too). Never
add or drop a block: the English book must have the same paragraphs as the Pāli, so that the § numbers,
the page anchors and the side-by-side view line up.

## Conventions

- **Page markers** `⟨pg:12⟩` (the Myanmar edition's pages) are copied into the English at the
  same place in the sentence, as near as the English allows. The build checks they are all there.
- **Lemmas.** The words being explained are kept in Pāli. In the Mūlaṭīkā they are the words of the Sammohavinodanī: use
  Ñāṇamoli's English for them (`data/dispeller.json`, at the same PTS page of the Sammohavinodanī) where
  it fits, and Thiṭṭila's (`data/thittila.json`, same §) for words of the Vibhaṅga itself. In the Anuṭīkā they are the words of the Mūlaṭīkā: use `mulatika/`. They are kept, in bold, as in the Pāli text, with the English in parentheses and quotes after
  them: `**karuṇā viyā** (“like compassion”)`. A lemma quoted with ‘‘…’’ in the Pāli keeps
  curly quotes: `**“dayāya tāya”** (“by that pity”)`.
- **Pāli words** discussed as words (etymologies, grammar) are in italics: *kirati*, *dayā*.
- **References** in parentheses (a. ni. 6.10; dha. sa. 985) are kept as they are in the Pāli.
- **Headings** keep the Pāli title, then · and the English: `Vīsatigāthāvaṇṇanā · Explanation
  of the Twenty Verses`.
- **Notes and supplied words** go in square brackets in the paragraph: [Buddhaghosa],
  [Objection:]. Use them sparingly.
- **[?]** marks a reading or a sense the translator is unsure of; say briefly why, in the same
  brackets: `[?: *word*, the reading is doubtful]`. The full list is in the last entry of `AUTOPILOT_LOG.md`.
- **Objections and replies** (*nanu …? — …*): mark the reply with an em dash; the views of
  others (*keci*, *apare*, *vadanti*) as "some say", "others", "they say".
- **Literal, not smooth.** Follow the argument and its grammar; keep *ti attho* as "the meaning
  is", *adhippāyo* as "the intention is", *sambandho* as "the connection is", *yojanā* as "the
  construction is".

## Terms

After Pe Maung Tin's *Expositor* (the translation of the Aṭṭhasālinī these explain), with
Khine and Rhys Davids where it has none. One term, one rendering, throughout both books.

| Pāli | English | Pāli | English |
|---|---|---|---|
| dhamma (state) | state | kusala | moral |
| akusala | immoral | abyākata | indeterminate |
| citta | consciousness (thought, where the text plays on it) | cetasika | mental property |
| cittuppāda | arising of consciousness | phassa | contact |
| vedanā | feeling | saññā | perception |
| cetanā | volition | vitakka | initial application |
| vicāra | sustained application | pīti | rapture |
| sukha | ease (pleasant feeling); happiness | ekaggatā | one-pointedness |
| paññā | wisdom | ñāṇa | knowledge |
| karuṇā | compassion | mettā | loving-kindness |
| dayā | pity | saddhā | faith |
| sati | mindfulness | samādhi | concentration |
| vīriya | energy | rūpa | matter (visible object: visible form) |
| khandha | aggregate | āyatana | base |
| dhātu | element | indriya | faculty |
| hetu | root (cause, in grammar and argument) | paccaya | condition |
| ārammaṇa | object | vipāka | resultant |
| kiriya | functional | lokiya / lokuttara | mundane / supramundane |
| kāmāvacara | of the sensuous sphere | rūpāvacara / arūpāvacara | of the fine-material / immaterial sphere |
| jhāna | jhāna | magga / phala | path / fruition |
| kilesa | defilement | āsava | canker |
| upakkilesa | corruption | nibbāna | Nibbāna |
| mātikā | matrix | pada | word; term |
| padabhājanīya | analysis of terms | uddesa / niddesa | summary / exposition |
| pāḷi | canonical text | aṭṭhakathā | commentary |
| saṃvaṇṇanā | explanation; exposition | sāmaññaphala | fruit of recluseship |
| paṭisambhidā | analytical insight | abhiññā | direct knowledge |
| tika / duka | triplet / couplet | gocchaka | group |
| anavajja / sāvajja | faultless / faulty | sukhavipāka / dukkhavipāka | of pleasant result / of painful result |
| upādāna | grasping | upādinna / upādāniya | grasped / favourable to grasping |
| rasa / paccupaṭṭhāna | function / manifestation | padaṭṭhāna | proximate cause |
| tadaṅga / vikkhambhana / samuccheda (pahāna) | (abandoning by) substitution of opposites / suppression / cutting off | kamma | kamma |
| saṃkilesa / saṃkiliṭṭha / saṃkilesika | corruption / corrupt / corruptible (the Expositor; *upakkilesa* is also "corruption") | upekkhā (feeling) | equanimity |
| dassana / bhāvanā (pahātabba) | (to be abandoned by) seeing / development (the Expositor: insight / culture) | ahetuka / sahetuka | rootless / with roots |
| sekkha / asekkha | of the trainee / beyond training (the Expositor: appertaining / not appertaining to studentship); sikkhā = training | ajjhatta / bahiddhā | internal / external (the Expositor: personal) |
| ānantariya (kamma) | (kamma) with immediate result | niyata / aniyata | fixed / not fixed (the Expositor: uniform) |
| sāsava | with cankers (the Expositor: co-intoxicant) | niyyānika | leading out |
| saraṇa / araṇa; raṇa | harmful / harmless; harm (the Expositor) | adhivacana / nirutti / paññatti (the couplets) | designation / explanation / description (the Expositor: synonym / etymology / expression) |
| nikkhepa(kaṇḍa) / atthuddhāra | (the) Summary / Extraction of the Meaning | hiri / ottappa | conscientiousness / fear of blame (the Expositor) |
| saṅkhāra | formation | paṭisandhi | rebirth-linking |
| anuppāda (ñāṇa) | (knowledge in) non-origination (the Expositor) | piṭṭhiduka | final couplet (the Expositor) |
| samaya / samavāya / khaṇa | occasion / harmony / moment (the Expositor); paccayasāmaggī = concurrence of conditions | ghana (vinibbhoga) | compact(ness) (resolution of compacts) |
| appanā (in the canonical text) | conclusion (the Expositor) | paññatti (time and the like) | concept (designated, for *paññatta*) |
| vatthukāma / kilesakāma | *kāma* as basis / *kāma* as defilement | kāmarāga / kāmataṇhā | sensual lust / sensual craving |
| somanassa / domanassa | joy / grief (the Expositor) | dhammārammaṇa | mental object |
| āpātha | avenue (the Expositor) | bhavaṅga | life-continuum (the Expositor) |
| javana | apperception (the Expositor) | asaṅkhārika / sasaṅkhārika | unprompted / prompted |
| dvāra / vatthu (of consciousness) | door / basis | vohāra | usage |
| nānatta / puthutta / pabheda / vavatthāna | difference / diversity / division / determination | liṅga | feature (the Expositor) |
| viññatti (kāya-, vacī-) | (body-, speech-) intimation (the Expositor) | copana (copanakāya) | movement (the moving body) |
| kāyakamma / vacīkamma / manokamma | bodily / vocal / mental kamma (the Expositor) | kammapatha | course of action (the Expositor) |
| saṃvara / asaṃvara | restraint / non-restraint (the Expositor) | duccarita / sucarita | misconduct / good conduct |
| abbohārika | negligible (the Expositor) | cetanāpakkhika | pertaining to volition (the Expositor) |
| dvārasaṃsandana / kammapathasaṃsandana | correlation of doors / of the courses of action | sanniṭṭhāpakacetanā | volition of decision (the Expositor) |
| mahābhūta / upādārūpa | great primary / derived matter | thambhana / upatthambhana | stiffening / strengthening (the Expositor: strengthens for both) |
| abhijjhā / anabhijjhā; byāpāda | covetousness / disinterestedness; ill-will (the Expositor) | dussīlya | immorality (the Expositor) |
| iddhi | potency (the Expositor) | upanissaya | decisive support |
| phassapañcamaka | contact pentad (the Expositor: fivefold contact-group) | rāsi | group |
| jhānaṅga / maggaṅga | jhāna factor / path factor | bala | strength (the Expositor) |
| saṅghaṭṭana / sannipāta | impact / coinciding (the Expositor) | tajjāsamannāhāra | suitable attention (the Expositor) |
| abhinipāta | incidence (the Expositor) | upacāra / appanā (in jhāna) | access / absorption |
| jīvitindriya | life-faculty (the Expositor) | sampajañña | comprehension (the Expositor) |
| passaddhi / lahutā / mudutā / kammaññatā / pāguññatā / ujukatā | repose / lightness / plasticity / wieldiness / fitness / rectitude (the Expositor) | samatha / vipassanā; paggāha / avikkhepa | calm / insight; uplift / non-distraction (the Expositor) |
| yevāpanaka | the "or whatever" states (the Expositor) | chanda / adhimokkha / manasikāra | desire / resolve / attention (the Expositor) |
| tatramajjhattatā | neutrality (there) (the Expositor: equanimity, balance of mind; kept apart from *upekkhā*) | uddhacca | excitement (the Expositor) |
| avibhattika / savibhattika | unclassifiable / classifiable (the Expositor) | apaṇṇakaṅga | universal factor (the Expositor) |
| viveka / vivekaja | aloofness / born of aloofness (the Expositor: aloof; born of solitude) | paṭipadā (sukhā / dukkhā) | (easy / painful) progress (the Expositor) |
| kasiṇa / abhibhāyatana | kasiṇa (the Expositor: device) / base of mastery (the Expositor: position of mastery) | vimokkha / brahmavihāra / asubha | deliverance / Divine State / the foul (the Expositor) |
| saṅkhārupekkhā | equanimity about formations | suññata / appaṇihita / animitta | emptiness / desireless (the Expositor: undesired) / signless |
| vuṭṭhānagāminī (vipassanā) | (insight) leading to emergence (the Expositor) | bojjhaṅga | factor of enlightenment (the Expositor: factor of wisdom) |
| nāmarūpa | mentality-materiality | paṭighasaññā / nānattasaññā | perception of impact / perception of difference (the Expositor) |
| pariyāya / nippariyāya (desanā) | figurative / non-figurative (teaching) | parikamma / pubbabhāga | preliminary work (the Expositor: preamble) / preparatory stage |
| pādakajjhāna / sammasitajjhāna | basic jhāna / contemplated jhāna (the Expositor); sammasati = contemplate | ajjhāsaya | inclination (the Expositor: personal inclination) |
| gotrabhu | change-of-lineage (the Expositor: adoption) | anuloma (ñāṇa) | conformity (the Expositor: adaptation) |
| anusaya | latent tendency (the Expositor: latent bias) | abhisaṅkhāraviññāṇa | formative consciousness (the Expositor: constructive consciousness) |
| āvajjana / sampaṭicchana | adverting / receiving (the Expositor) | santīraṇa / voṭṭhabbana | examining / determining (the Expositor) |
| tadārammaṇa | registration (the Expositor) | moghavāra | ineffectual occasion (the Expositor) |
| tihetuka / duhetuka | three-rooted / two-rooted (the Expositor: thrice- / twice-conditioned) | iṭṭhamajjhatta | moderately desirable (the Expositor) |
| piṇḍajavana | mass-apperception (the Expositor) | niyāma (bīja-, utu-, kamma-, dhamma-, citta-) | order (the Expositor) |
| vipākuddhāra | elucidating results (the Expositor) | saṅgahavāra | section of the compendium (the Expositor: of the Summary) |
| nānākkhaṇika (kammapaccaya) | asynchronous (kamma condition) | āsevana (paccaya) | repetition (condition) |
| pakiṇṇaka (duka) | miscellaneous (couplet) (the Expositor: special case) | ekaka (saṅgaha); rūpavibhatti | unitary (compendium) (the Expositor); classification of matter |
| kalāpa | group (of matter) | saṅgaha (rūpa-) | compendium (the Expositor) |
| pasāda (cakkhu- etc.) | sentient organ (the Expositor) | utu | temperature (the Expositor: caloric order) |
| kaṭattārūpa | kamma-produced matter | parinipphanna / aparinipphanna | produced / unproduced (the Expositor: predetermined / unpredetermined) |
| ariya / puthujjana | noble one / worldling (the Expositor: Ariyan / average man) | sakkāyadiṭṭhi | personality view (the Expositor: theory of individuality) |
| sahajekaṭṭha / pahānekaṭṭha | united in co-existence / united in abandoning (the Expositor: in removal) | ahetuka- / akiriya- / natthikavāda | doctrine of non-causality / of the inefficacy of action / of nihilism |
| kāmāsava / bhavāsava / diṭṭhāsava / avijjāsava | canker of sensuality / of existence / of views / of ignorance (the Expositor: intoxicant of sensuality / rebirth / views / ignorance) | nīvaraṇa; thinamiddha; kukkucca | hindrance; sloth and torpor; worry (the Expositor) |
| saṅkhā / samaññā / vohāra (adhivacana series) | utterance / appellation / usage (the Expositor: utterance / designation / current term) | nāmakamma / nāmadheyya / byañjana / abhilāpa | denomination / name-assigning / distinctive mark / signification (the Expositor) |
| upādāpaññatti / nāmapaññatti | derived concept / name-concept | vijjamāna- / avijjamānapaññatti; paññattipatha | concept of the existent / of the non-existent; pathway of concept |
| sammutisacca | conventional truth | kammavācā | ecclesiastical vote (the Expositor) |
| aṭṭhakathākaṇḍa | the Commentarial Section (the Expositor: Commentarial Chapter) | navattabba(ārammaṇa) | (with an object) not to be spoken of (the Expositor: undefinable) |
| khaṇa- / santati- / addhāpaccuppanna | momentary / continuous / durational present (the Expositor) | kammanimitta / gatinimitta | sign of kamma / sign of destiny (the Expositor: kamma-symbol / tendency-symbol) |
| cetopariyañāṇa / pubbenivāsānussatiñāṇa | knowledge of others' minds / of the recollection of former lives (the Expositor: of others' thoughts / of former lives) | yathākammūpagañāṇa / anāgataṃsañāṇa / iddhividha | knowledge of passing according to kamma / of the future; (knowledge of) the kinds of potency (the Expositor: destiny of one's actions / future / variety of potency) |
| sabbatthapādaka | basis for everything (the Expositor: everywhere a vantage-point) | vipākadhammadhamma | (state that is a) cause of results |
| rūparūpa | concrete matter | aṅga (sutta-, geyya- etc.) | factor (of the ninefold word of the Buddha) |
| hāra / naya (of the Netti) | mode of conveying / method (after Ñāṇamoli, *The Guide*: desanā- teaching, vicaya investigation, yutti construing, …; nandiyāvatta conversion of relishing, tipukkhala trefoil, sīhavikkīḷita lion's play) | sāsanapaṭṭhāna | pattern of the Dispensation |
| saṃyojana / gantha / ogha / yoga / parāmāsa (gocchaka) | fetter / knot / flood / bond / reversion (group) (the Expositor) | saṃyojaniya / nīvaraṇiya; parāmaṭṭha | favourable to fetters / to hindrances; reversed (the Expositor) |

Words were checked against the Digital Pāḷi Dictionary (Bodhirasa Bhikkhu, dpdict.net,
CC BY-NC-SA 4.0).

## Tools

- `python3 scripts/translation/show.py sammoha 3` prints the Pāli of part 3 with block numbers.
- `python3 scripts/translation/dpd.py word …` looks words up in the Digital Pāḷi Dictionary. The
  subset in `dpd-tika.sqlite.gz` was made for the Dhammasaṅgaṇī's commentaries, so a word it lacks is
  not necessarily rare.

The translation is made by the scheduled autopilot, one chunk per run (see `AUTOPILOT.md` and
`AUTOPILOT_LOG.md`).
