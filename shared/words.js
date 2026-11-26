/* Short meanings of Pāli words: hover (or tap) a word to see the English the translators of
   the library give it. The words and their English are search/terms.json (scripts/build_search.py:
   a core list and Khine's index, kept only where the books use them). Used by the books
   (shared/reader.js loads this file) and by compare/.

   PaliWords.init(base)        load the list (base: the path to the library root, '../')
   PaliWords.mark(el, slug)    underline the known words in el (a part of a book just loaded)
   PaliWords.meaning(word)     {pali, en:[...]} for a word in any form, or null */
(function(){
  'use strict';
  if(window.PaliWords) return;
  const MAP={'ā':'a','ī':'i','ū':'u','ṃ':'m','ṁ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l','ṛ':'r','ś':'s','ṣ':'s','ç':'s','ḥ':'h','â':'a','î':'i','û':'u'};
  const norm=s=>s.toLowerCase().replace(/[āīūṃṁṅñṭḍṇḷṛśṣçḥâîû]/g,c=>MAP[c]);
  const DIAC=/[āīūṃṁṅñṭḍṇḷâîûĀĪŪṂṀṄÑṬḌṆḶ]/;
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  /* the books written in Pāli: every known word is marked; in the English books only a word in
     italics, with a diacritic, or written out as the dictionary form (phassa) */
  const PALI_BOOKS=/^(pali|muller|atthasalini|mulatika|anutika)$/;
  /* the endings a word may carry, by the vowel of its stem: phasso, phassaṃ, phassena (a);
     vedanāya (ā); satiyā (i); dhātuyo (u) */
  const ENDS=[
    ['a',['asmiṃ','assa','ānaṃ','ehi','esu','ena','āya','āni','ato','amhi','aṃ','o','ā','e']],
    ['ā',['āyo','āya','ānaṃ','āsu','aṃ']],
    ['i',['iyā','iyo','īnaṃ','issa','inā','iṃ','ī','ayo']],
    ['u',['uyā','uyo','ūnaṃ','ussa','unā','uṃ','ū','avo']]];
  /* one sound, one letter: Müller writes â, Khine ṁ */
  const FOLD={'â':'ā','î':'ī','û':'ū','ṁ':'ṃ'};
  const fold=s=>s.toLowerCase().replace(/[âîûṁ]/g,c=>FOLD[c]);
  const LETTERS=/[^a-zāīūṃṅñṭḍṇḷ]/g;
  let T=null, PLAIN=null, P=null, BASE='../';

  function init(base){
    if(base) BASE=base;
    if(!P) P=fetch(BASE+'search/terms.json').then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); }).then(j=>{
      T=new Map(); PLAIN=new Map();
      j.t.forEach(([p,rs])=>{
        const k=fold(p).replace(LETTERS,''); if(k.length<3) return;
        if(!T.has(k)) T.set(k,{pali:p, en:[]});
        const e=T.get(k); rs.forEach(r=>{ if(!e.en.includes(r[0])) e.en.push(r[0]); });
        const n=norm(k); if(!PLAIN.has(n)) PLAIN.set(n,k);
      });
    }).catch(()=>{ P=null; });
    return P;
  }
  /* the dictionary form of a word as the books print it, or null */
  function key(w){
    if(!T) return null;
    if(T.has(w)) return w;
    for(const [v,ends] of ENDS) for(const e of ends){
      if(w.length-e.length<3||!w.endsWith(e)) continue;
      const k=w.slice(0,-e.length)+v; if(T.has(k)) return k;
    }
    if(!DIAC.test(w) && PLAIN.has(w)) return PLAIN.get(w);   /* written without diacritics: vedana */
    return null;
  }
  function meaning(w){ const k=key(fold(w).replace(LETTERS,'')); return k?T.get(k):null; }

  const SKIP='a,button,script,style,mark,sup,h1,h2,h3,th,.sh,.pnum,.crumbs,.eyebrow,summary,.tiphead,.pw,.xb,.ptsp,select,input,textarea';
  function mark(el,slug){
    if(!T||!el||el._pw) return 0;
    el._pw=true;
    const pali=PALI_BOOKS.test(slug||'');
    const walk=document.createTreeWalker(el,NodeFilter.SHOW_TEXT,{acceptNode:n=>!n.data.trim()||n.parentElement.closest(SKIP)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
    const nodes=[]; while(walk.nextNode()) nodes.push(walk.currentNode);
    let n=0;
    nodes.forEach(t=>{
      const s=t.data, low=fold(s); if(low.length!==s.length) return;
      const re=/[a-zāīūṃṅñṭḍṇḷ­]+/g; let m, at=0, frag=null;
      const ital=!pali&&!!t.parentElement.closest('i,em');
      while((m=re.exec(low))){
        const w=m[0].replace(/­/g,''); if(w.length<3) continue;
        const k=key(w); if(!k) continue;
        const orig=s.slice(m.index,m.index+m[0].length);
        if(!pali && !ital && !DIAC.test(orig) && !(norm(w)===norm(k)&&k.length>=5)) continue;
        if(!frag) frag=document.createDocumentFragment();
        frag.append(s.slice(at,m.index));
        const sp=document.createElement('span'); sp.className='pw'; sp.dataset.k=k; sp.textContent=orig; frag.append(sp);
        at=m.index+m[0].length; n++;
      }
      if(frag){ frag.append(s.slice(at)); t.replaceWith(frag); }
    });
    return n;
  }

  /* the tip: on hover, or pinned by a click or tap with links to search and to the terms */
  let tip=null, pinned=false;
  function body(e,word,pin){
    const shown=e.en.slice(0,6);
    return '<div class="tiphead">'+esc(e.pali)+(fold(word).replace(LETTERS,'')!==fold(e.pali).replace(LETTERS,'')?' <em>('+esc(word)+')</em>':'')+'</div>'+
      '<div class="pwmean">'+shown.map(esc).join(' · ')+(e.en.length>shown.length?' …':'')+'</div>'+
      (pin?'<div class="pwlinks"><a href="'+BASE+'search/?q='+encodeURIComponent(e.pali)+'">Search the library →</a><a href="'+BASE+'terms/?q='+encodeURIComponent(e.pali)+'">Pāli terms →</a></div>':'<div class="pwhint">The English the translators of the library use. Click for more.</div>');
  }
  function place(t,a){
    document.body.appendChild(t);
    const r=a.getBoundingClientRect(), w=t.offsetWidth, h=t.offsetHeight;
    const x=Math.max(8,Math.min(innerWidth-w-8,r.left+r.width/2-w/2));
    let y=r.bottom+8; if(y+h>innerHeight-8) y=Math.max(8,r.top-h-8);
    t.style.left=x+'px'; t.style.top=y+'px';
  }
  function show(a,pin){
    hide(); const e=T&&T.get(a.dataset.k); if(!e) return;
    tip=document.createElement('div'); tip.className='tip pwtip'+(pin?' pinned':''); tip.setAttribute('role','tooltip');
    tip.innerHTML=body(e,a.textContent,pin); place(tip,a); pinned=!!pin;
  }
  function hide(){ if(tip){ tip.remove(); tip=null; pinned=false; } }
  const touch=()=>matchMedia('(hover: none)').matches;
  document.addEventListener('mouseover',e=>{ if(touch()||pinned) return; const a=e.target.closest('span.pw'); if(a) show(a,false); });
  document.addEventListener('mouseout',e=>{ if(!pinned && e.target.closest('span.pw')) hide(); });
  document.addEventListener('click',e=>{
    const a=e.target.closest('span.pw');
    if(a){ e.preventDefault(); show(a,true); return; }
    if(tip && !e.target.closest('.pwtip')) hide();
  });
  document.addEventListener('keydown',e=>{ if(e.key==='Escape') hide(); });
  addEventListener('scroll',hide,{passive:true,capture:true});
  addEventListener('resize',hide);

  /* an index word of the book (a.vw, a link to the book's index drawer) where there is no drawer:
     a plain word, with its meaning if the list has one */
  function unlink(el){
    el.querySelectorAll('a.vw').forEach(a=>{
      const k=key(fold(a.dataset.k||a.textContent).replace(LETTERS,''));
      const sp=document.createElement('span'); sp.className=k?'pw':'vwx'; if(k) sp.dataset.k=k;
      while(a.firstChild) sp.appendChild(a.firstChild);
      a.replaceWith(sp);
    });
  }
  window.PaliWords={init, mark, meaning, unlink};
})();
