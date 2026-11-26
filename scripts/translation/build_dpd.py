"""Rebuild dpd-tika.sqlite.gz: clone github.com/digitalpalidictionary/dpd-db (GIT_LFS_SKIP_SMUDGE=1, --depth 1)
to /home/claude/digitalpalidictionary/dpd-db, run this, then the compacting step in AUTOPILOT.md. CC BY-NC-SA 4.0."""
csv.field_size_limit(10**9)
LIB='/home/claude/dhammasangani-library'
forms=collections.Counter()
for s in ('mulatika','anutika'):
    d=json.load(open(f'{LIB}/data/{s}.json'))
    for ch in d['chapters']:
        for b in ch['blocks']:
            t=re.sub(r'⟨[^⟩]*⟩|\*\*','',b['text']).lower()
            forms.update(re.findall(r"[a-zāīūṃṅñṭḍṇḷ]+",t))
print('unique forms',len(forms),file=sys.stderr)
db=sqlite3.connect('/home/claude/tools/dpd.sqlite'); c=db.cursor()
c.executescript('drop table if exists hw; drop table if exists inf; create table hw(id integer primary key, lemma text, pos text, grammar text, meaning text, lit text, construction text, compound text); create table inf(form text, id integer); ')
n=0
for f in sorted(glob.glob('/home/claude/digitalpalidictionary/dpd-db/db/backup_tsv/dpd_headwords_part_*.tsv')):
    with open(f,encoding='utf-8') as fh:
        for r in csv.DictReader(fh,delimiter='\t'):
            m=r['meaning_1'] or r['meaning_2']
            c.execute('insert into hw values(?,?,?,?,?,?,?,?)',(int(r['id']),r['lemma_1'],r['pos'],r['grammar'],m,r['meaning_lit'],r['construction'],r['compound_construction']))
            infl=set(x for x in r['inflections_api_ca_eva_iti'].split(',') if x)
            l2=r['lemma_2'] or r['lemma_1'].split(' ')[0]; infl.add(l2)
            for x in infl:
                if x in forms: c.execute('insert into inf values(?,?)',(x,int(r['id']))); n+=1
c.execute('create index i1 on inf(form)'); db.commit()
found=set(x for (x,) in c.execute('select distinct form from inf'))
print('form links',n,'forms covered',len(found),'of',len(forms), 'tokens covered %.1f%%'%(100*sum(forms[f] for f in found)/sum(forms.values())),file=sys.stderr)

# ---- every inflected form, from the stem and the pattern's template
TPL='/home/claude/digitalpalidictionary/dpd-db/db/inflections/templates'
import os
templates={}
for fn in os.listdir(TPL):
    rows=list(csv.reader(open(os.path.join(TPL,fn),encoding='utf-8'),delimiter='\t'))
    ends=set()
    for row in rows[1:]:
        for i in range(1,len(row),2):
            for e in row[i].split(','):
                e=e.strip()
                if e or row[i]=='' : ends.add(e)
    templates[fn[:-4]]=ends
n2=0
for f in sorted(glob.glob('/home/claude/digitalpalidictionary/dpd-db/db/backup_tsv/dpd_headwords_part_*.tsv')):
    with open(f,encoding='utf-8') as fh:
        for r in csv.DictReader(fh,delimiter='\t'):
            st=r['stem'].lstrip('!'); pat=r['pattern']
            if not st or st=='-' or pat not in templates: continue
            for e in templates[pat]:
                x=st+e
                if x in forms: c.execute('insert into inf values(?,?)',(x,int(r['id']))); n2+=1
db.commit()
found=set(x for (x,) in c.execute('select distinct form from inf'))
print('with templates: links',n2,'forms covered',len(found),'of',len(forms),'tokens covered %.1f%%'%(100*sum(forms[f] for f in found)/sum(forms.values())),file=sys.stderr)
json.dump(sorted(forms.items(),key=lambda x:-x[1]),open('/home/claude/tools/tika_forms.json','w'),ensure_ascii=False)
