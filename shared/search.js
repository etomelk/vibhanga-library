/* Library search: every book at once, with the Pāli words and the English of the translators
   searched together. The books' own indexes (<slug>/search.json) are loaded as soon as the page
   opens and the results grow as each one arrives. The term list is search/terms.json, written by
   scripts/build_search.py. */
(function(){
  'use strict';
  const root=document.documentElement;
  try{const t=localStorage.getItem('pg-theme'); if(t) root.setAttribute('data-theme',t);}catch(e){}
  document.getElementById('themebtn').addEventListener('click',()=>{
    const dark=root.getAttribute('data-theme')==='dark'||(!root.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
    const next=dark?'light':'dark'; root.setAttribute('data-theme',next); try{localStorage.setItem('pg-theme',next);}catch(e){}
  });

  const LIB=window.LIB, BOOKS=LIB.books, SHELVES=LIB.shelves;
  const $=s=>document.querySelector(s);
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const MAP={'ā':'a','ī':'i','ū':'u','ṃ':'m','ṁ':'m','ṅ':'n','ñ':'n','ṭ':'t','ḍ':'d','ṇ':'n','ḷ':'l','ṛ':'r','ś':'s','ṣ':'s','ç':'s','ḥ':'h','â':'a','î':'i','û':'u'};
  /* one character in, one character out, so that positions in the normalised text are positions in the text */
  const norm=s=>s.toLowerCase().replace(/[āīūṃṁṅñṭḍṇḷṛśṣçḥâîû]/g,c=>MAP[c]);
  const reEsc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const B='(?<![a-z0-9])', E='(?![a-z0-9])';

  /* ---- the books' indexes */
  const units={};            /* slug -> [{id,text,n,where}] */
  let loaded=0;
  const loading=BOOKS.map(b=>fetch('../'+b.slug+'/search.json').then(r=>{ if(!r.ok) throw r.status; return r.json(); }).then(j=>{
    units[b.slug]=j.u.map(x=>{ const c=j.ch[x[0]], t=x[2].replace(/\u00ad/g,''); return {id:x[1], text:t, n:norm(t), where:c[0]+' · '+c[1]+(x[3]?' · '+x[3]:'')}; });
  }).catch(()=>{ units[b.slug]=null; }).finally(()=>{ loaded++; schedule(true); }));

  /* ---- the term list */
  const byPali=new Map(), byEng=new Map();     /* normalised -> entries */
  let termsReady=fetch('terms.json').then(r=>r.json()).then(j=>{
    j.t.forEach(([p,rs])=>{
      const ent={pali:p, key:norm(p), eng:rs.map(([r,t])=>({r, n:norm(r), trigger:!!t}))};
      byPali.set(ent.key,ent);
      ent.eng.forEach(x=>{ if(!x.trigger) return; const a=byEng.get(x.n)||[]; a.push(ent); byEng.set(x.n,a); });
    });
  }).catch(()=>{}).finally(()=>schedule(true));

  function paliLookup(w){
    if(byPali.has(w)) return byPali.get(w);
    /* phasso, phassaṃ, phassena -> phassa */
    const m=w.match(/^(.{3,}?)(o|am|ena|assa|ani|aya|e|ehi|esu|anam|a)$/);
    if(m && byPali.has(m[1]+'a')) return byPali.get(m[1]+'a');
    return null;
  }
  function engLookup(w){
    return byEng.get(w)||(w.endsWith('s')&&byEng.get(w.slice(0,-1)))||(w.endsWith('es')&&byEng.get(w.slice(0,-2)))||null;
  }

  /* a pattern for an added word: English as a whole word (with a plural), Pāli with its endings
     (long words also in compounds: rūpakkhandha) */
  function altPattern(n,isPali){
    const words=n.split(/\s+/).map(reEsc).join('[\\s-]+');
    if(!isPali) return B+words+'(?:s|es)?'+E;
    if(/\s/.test(n)) return B+words;
    if(n.length>=5 || /o$/.test(n)) return B+reEsc(n.replace(/[aiu]$/,''))+'[a-z]*';
    const stem=n.replace(/[a]$/,'');
    return B+reEsc(stem)+'(?:a|o|am|e|ena|assa|aya|ani|ehi|esu|anam|ato|aya|i|u)?'+E;
  }

  /* ---- the query: groups of alternatives, every group must match */
  const off=new Set();       /* added words the reader switched off */
  const onx=new Set();       /* common words (form, matter) the reader switched on: they start off */
  function parse(raw){
    const groups=[]; const s=raw.replace(/[“”]/g,'"');
    const phrases=[]; const rest=s.replace(/"([^"]+)"/g,(_,p)=>{ phrases.push(p.trim()); return ' '; });
    phrases.filter(Boolean).forEach(p=>groups.push(group(norm(p),true)));
    const words=norm(rest).split(/\s+/).filter(w=>w.length>0);
    if(words.length>1){ const whole=words.join(' '); if(byPali.has(whole)||engLookup(whole)){ groups.push(group(whole,false)); return groups; } }
    words.forEach(w=>groups.push(group(w,false)));
    return groups.filter(g=>g.orig.length>=2);
  }
  function group(w,exact){
    const g={orig:w, exact, alts:[], via:[]};
    if(!exact || /\s/.test(w)){
      const seen=new Set([w]);
      const add=(n,label,isPali,common)=>{ if(seen.has(n)) return; seen.add(n); g.alts.push({n,label,isPali,common:!!common,on:common?onx.has(n):!off.has(n)}); };
      const p=paliLookup(w);
      if(p){ g.via.push(p.pali); add(p.key,p.pali,true); p.eng.forEach(x=>add(x.n,x.r,false,!x.trigger)); }
      const es=engLookup(w);
      if(es) es.forEach(ent=>{ g.via.push(ent.pali); add(ent.key,ent.pali,true); ent.eng.forEach(x=>add(x.n,x.r,false,!x.trigger)); });
    }
    g.re=new RegExp(exact||/\s/.test(w)?B+w.split(/\s+/).map(reEsc).join('[\\s-]+')+E:reEsc(w),'g');
    g.whole=new RegExp(B+reEsc(w)+E);
    const on=g.alts.filter(a=>a.on);
    g.altRe=on.length?new RegExp(on.map(a=>altPattern(a.n,a.isPali)).join('|'),'g'):null;
    return g;
  }

  /* ---- search */
  function scoreUnit(u,groups){
    let score=0;
    for(const g of groups){
      g.re.lastIndex=0;
      if(g.re.test(u.n)){ score+=g.whole.test(u.n)?14:10; continue; }
      if(g.altRe){ g.altRe.lastIndex=0; if(g.altRe.test(u.n)){ score+=5; continue; } }
      return 0;
    }
    return score+(u.n.length<160?1:0);
  }
  function spans(u,groups){
    const out=[];
    groups.forEach(g=>[g.re,g.altRe].forEach(re=>{ if(!re) return; re.lastIndex=0; let m; while((m=re.exec(u.n))){ if(!m[0].length){re.lastIndex++;continue;} out.push([m.index,m.index+m[0].length]); } }));
    out.sort((a,b)=>a[0]-b[0]);
    const merged=[]; out.forEach(s=>{ const l=merged[merged.length-1]; if(l&&s[0]<=l[1]) l[1]=Math.max(l[1],s[1]); else merged.push(s.slice()); });
    return merged;
  }
  function snippet(u,groups){
    const sp=spans(u,groups), t=u.text;
    const first=sp.length?sp[0][0]:0;
    const s=first>90?t.lastIndexOf(' ',first-80)+1||first-80:0;
    let e=Math.min(t.length,s+260); if(e<t.length){ const sp2=t.indexOf(' ',e); e=sp2>0&&sp2<e+30?sp2:e; }
    let h='', at=s;
    sp.forEach(([a,b])=>{ if(b<=s||a>=e) return; a=Math.max(a,s); b=Math.min(b,e); h+=esc(t.slice(at,a))+'<mark>'+esc(t.slice(a,b))+'</mark>'; at=b; });
    h+=esc(t.slice(at,e));
    return (s>0?'… ':'')+h+(e<t.length?' …':'');
  }

  /* ---- state, URL */
  const params=new URLSearchParams(location.search);
  const q=$('#sq'); q.value=params.get('q')||'';
  let shelf=params.get('shelf')||'all', book=params.get('book')||'', shown={};
  const from=params.get('from');

  const shelvesEl=$('#shelves');
  shelvesEl.innerHTML='<button type="button" data-shelf="all">All books</button>'+SHELVES.map((s,i)=>'<button type="button" data-shelf="'+i+'" title="'+esc(s.name)+'">'+esc(s.short)+'</button>').join('');
  shelvesEl.addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; shelf=b.dataset.shelf; book=''; shown={}; run(); });

  const EX=['phassa','feeling','“mental factors”','lobha','initial application','rūpa','vedanā cetanā','nīvaraṇa'];
  $('#examples').innerHTML=EX.map(x=>'<button type="button" class="mchip">'+esc(x)+'</button>').join('');
  $('#examples').addEventListener('click',e=>{ const b=e.target.closest('button'); if(!b) return; q.value=b.textContent; off.clear(); shown={}; run(); q.focus(); });

  $('#sform').addEventListener('submit',e=>{ e.preventDefault(); run(); const f=document.querySelector('#sresults a.hit'); if(f && innerWidth<700) q.blur(); });
  let t=null; q.addEventListener('input',()=>{ clearTimeout(t); off.clear(); onx.clear(); shown={}; book=''; t=setTimeout(run,220); });
  document.addEventListener('keydown',e=>{ if(e.key==='/' && !/INPUT|TEXTAREA/.test(document.activeElement.tagName)){ e.preventDefault(); q.focus(); q.select(); } });

  $('#expand').addEventListener('click',e=>{ const b=e.target.closest('button[data-n]'); if(!b) return; const n=b.dataset.n, was=b.getAttribute('aria-pressed')==='true'; if(b.dataset.common){ if(was) onx.delete(n); else onx.add(n); } else { if(was) off.add(n); else off.delete(n); } run(); });
  $('#bookbar').addEventListener('click',e=>{ const b=e.target.closest('button[data-book]'); if(!b) return; book=book===b.dataset.book?'':b.dataset.book; shown={}; run(); window.scrollTo({top:$('#bookbar').offsetTop-70}); });
  $('#sresults').addEventListener('click',e=>{
    const b=e.target.closest('button[data-more]'); if(!b) return;
    const s=b.dataset.more; if(!book){ book=s; shown={}; run(); window.scrollTo({top:$('#bookbar').offsetTop-70}); } else { shown[s]=(shown[s]||50)+100; run(true); }
  });

  let pend=null;
  function schedule(){ if(pend) return; pend=requestAnimationFrame(()=>{ pend=null; run(true); }); }

  function syncURL(){
    const p=new URLSearchParams(); const v=q.value.trim();
    if(v) p.set('q',v); if(shelf!=='all') p.set('shelf',shelf); if(book) p.set('book',book); if(from) p.set('from',from);
    const u=location.pathname+(p.toString()?'?'+p:''); if(u!==location.pathname+location.search) history.replaceState(null,'',u);
    document.title=(v?'“'+v+'” · ':'')+'Search · '+document.title.split(' · ').slice(-1)[0];
  }

  function run(keep){
    const raw=q.value.trim();
    shelvesEl.querySelectorAll('button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.shelf===shelf)));
    syncURL();
    const groups=raw?parse(raw):[];
    document.body.classList.toggle('has-q',!!groups.length);
    $('#sempty').hidden=!!groups.length;
    const status=$('#sstatus'), out=$('#sresults'), bar=$('#bookbar'), ex=$('#expand');
    if(!groups.length){ out.innerHTML=''; bar.hidden=true; ex.hidden=true; status.textContent=raw?'Type at least two letters.':(loaded<BOOKS.length?'Loading the books… '+loaded+' of '+BOOKS.length:''); return; }

    /* the words added to the search, each one can be switched off */
    const alts=[]; groups.forEach(g=>g.alts.forEach(a=>alts.push(a)));
    if(alts.length){
      const via=[...new Set(groups.flatMap(g=>g.via))];
      ex.hidden=false;
      ex.innerHTML='<span class="exlab">Also searching'+(via.length?' <a href="../terms/?q='+encodeURIComponent(via[0])+'" class="exvia" title="See the word in the list of Pāli terms">('+via.map(esc).join(', ')+')</a>':'')+':</span> '+
        alts.map(a=>'<button type="button" class="exchip'+(a.isPali?' pali':'')+'" data-n="'+esc(a.n)+'"'+(a.common?' data-common="1"':'')+' aria-pressed="'+a.on+'" title="'+(a.on?'Click to leave this word out':'Click to search this word too')+'">'+esc(a.label)+'</button>').join('')+
        '<span class="exnote">'+(alts.some(a=>!a.on)?'Crossed-out words are left out (too common, or switched off): tap one to add it.':'Tap a word to leave it out.')+'</span>';
    } else ex.hidden=true;

    const res=[]; let total=0, nb=0;
    BOOKS.forEach(b=>{
      const us=units[b.slug]; const inShelf=shelf==='all'||String(b.shelf)===shelf;
      if(!us){ res.push({b, hits:null, inShelf}); return; }
      const hits=[]; us.forEach((u,i)=>{ const s=scoreUnit(u,groups); if(s) hits.push({u,s,i}); });
      hits.sort((a,c)=>c.s-a.s||a.i-c.i);
      res.push({b,hits,inShelf});
      if(inShelf){ total+=hits.length; if(hits.length) nb++; }
    });

    const hl=encodeURIComponent([...new Set(groups.flatMap(g=>[g.orig].concat(g.alts.filter(a=>a.on).map(a=>a.n))))].join('|'));
    const pending=BOOKS.length-loaded;
    status.innerHTML=(total?'<b>'+total.toLocaleString()+'</b> passage'+(total===1?'':'s')+' in <b>'+nb+'</b> book'+(nb===1?'':'s'):'No passages found')+
      (shelf!=='all'?' on the shelf <i>'+esc(SHELVES[+shelf].name)+'</i> · <button type="button" class="linkbtn" id="allsh">search all books</button>':'')+
      (pending?' <span class="sload">· loading '+pending+' more book'+(pending===1?'':'s')+'…</span>':'');
    const a=$('#allsh'); if(a) a.onclick=()=>{ shelf='all'; run(); };

    bar.hidden=false;
    bar.innerHTML=res.filter(r=>r.inShelf).map(r=>{
      const n=r.hits?r.hits.length:null;
      return '<button type="button" data-book="'+r.b.slug+'" aria-pressed="'+(book===r.b.slug)+'"'+(n===0?' class="zero"':'')+' title="'+esc(r.b.title)+'">'+esc(r.b.cite)+' <span>'+(n===null?(units[r.b.slug]===null?'×':'…'):n.toLocaleString())+'</span></button>';
    }).join('');

    const html=[];
    const order=from&&!book?res.slice().sort((x,y)=>(y.b.slug===from)-(x.b.slug===from)):res;
    order.forEach(r=>{
      if(!r.inShelf||!r.hits||!r.hits.length) return;
      if(book && r.b.slug!==book) return;
      const lim=book?(shown[r.b.slug]||50):4;
      const list=r.hits.slice(0,lim).map(h=>
        '<a class="hit" href="../'+r.b.slug+'/?hl='+hl+'#'+encodeURIComponent(h.u.id)+'"><span class="where">'+esc(h.u.where)+'</span><span class="snip">'+snippet(h.u,groups)+'</span></a>').join('');
      const more=r.hits.length>lim?'<button type="button" class="more" data-more="'+r.b.slug+'">'+(book?'Show more ('+(r.hits.length-lim).toLocaleString()+' left)':'All '+r.hits.length.toLocaleString()+' passages in '+esc(r.b.cite)+' →')+'</button>':'';
      html.push('<section class="rbook'+(r.b.slug===from&&!book?' from':'')+'"><header><h2><a href="../'+r.b.slug+'/">'+esc(r.b.cite)+'</a></h2><p>'+esc(r.b.title)+' · <span>'+esc(SHELVES[r.b.shelf].short)+'</span></p><span class="rcount">'+r.hits.length.toLocaleString()+'</span></header>'+list+more+'</section>');
    });
    if(!html.length && total===0 && !pending){
      html.push('<p class="snone">Nothing in '+(shelf==='all'?'the library':'these books')+' matches every word. Try fewer words, or part of a word: <i>vipak</i> finds <i>vipāka</i> and <i>vipākā</i>.</p>');
    }
    if(!keep||out.innerHTML!==html.join('')) out.innerHTML=html.join('');
  }

  Promise.all([termsReady]).then(()=>run());
})();
