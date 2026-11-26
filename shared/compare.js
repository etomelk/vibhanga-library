/* Two books side by side (compare/). Each side shows one part of a book at a time, loaded from the
   book's own files (index.html for its parts, ids.json for where each id is, c/<part>.html for the
   text). compare/<slug>.json, written by scripts/build_compare.py, says which place in the other
   book lines up with each place in this one; as one side is scrolled the other follows. */
(function(){
  'use strict';
  const root=document.documentElement;
  try{const t=localStorage.getItem('pg-theme'); if(t) root.setAttribute('data-theme',t);}catch(e){}
  document.getElementById('themebtn').addEventListener('click',()=>{
    const dark=root.getAttribute('data-theme')==='dark'||(!root.getAttribute('data-theme')&&matchMedia('(prefers-color-scheme: dark)').matches);
    const next=dark?'light':'dark'; root.setAttribute('data-theme',next); try{localStorage.setItem('pg-theme',next);}catch(e){}
  });

  const BOOKS=window.LIB.books, BY={}; BOOKS.forEach(b=>BY[b.slug]=b);
  const $=(s,el)=>(el||document).querySelector(s);
  const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const byId=(el,id)=>el.querySelector('[id="'+id.replace(/"/g,'\\"')+'"]');
  const narrow=()=>matchMedia('(max-width:760px)').matches;
  const text=u=>fetch(u).then(r=>{ if(!r.ok) throw new Error(r.status); return r.text(); });

  /* ---- a book: its parts, where each id is, and what lines up with what */
  const cache={};
  function book(slug){
    if(!cache[slug]) cache[slug]=Promise.all([
      text('../'+slug+'/index.html'), text('../'+slug+'/ids.json'), text(slug+'.json').catch(()=>'{"ids":[],"to":{},"chs":[],"c":[]}')
    ]).then(([html,ids,cmp])=>{
      const doc=new DOMParser().parseFromString(html,'text/html');
      const chapters=[...doc.querySelectorAll('section.chapter')].map(s=>({id:s.id, label:s.dataset.label||'', title:s.dataset.title||'', src:s.dataset.src||null, html:s.dataset.src?null:s.innerHTML}));
      const B={slug, chapters, chap:{}, where:JSON.parse(ids), cmp:JSON.parse(cmp), sign:doc.documentElement.dataset.sign||'', parts:{}};
      chapters.forEach((c,i)=>{ B.chap[c.id]=i; });
      B.mi={}; B.cmp.ids.forEach((id,i)=>{ if(!(id in B.mi)) B.mi[id]=i; });
      return B;
    });
    return cache[slug];
  }
  function part(B,ch){
    const c=B.chapters[B.chap[ch]];
    if(!B.parts[ch]) B.parts[ch]=c.src?text('../'+B.slug+'/'+c.src):Promise.resolve(c.html||'');
    return B.parts[ch];
  }
  function chapterOf(B,id){ if(id in B.chap) return id; return B.where[id]||null; }

  /* a short name for a place: §58, p. 163, Mātikā t1 */
  function ref(B,id){
    let m;
    if((m=id.match(/^p(\d+)$/))) return (B.sign||'§')+m[1];
    if((m=id.match(/^pgP(\w+)$/))) return 'PTS p. '+m[1];
    if((m=id.match(/^pg(\w+)$/))) return 'p. '+m[1];
    if((m=id.match(/^a(\d+)$/))) return 'PTS p. '+m[1];
    if((m=id.match(/^m([tds])(\d+)$/))) return 'Mātikā '+m[1]+m[2];
    return '';
  }

  /* ---- a side */
  function Pane(el,name){
    this.el=el; this.name=name; this.B=null; this.ch=null; this.lock=0;
    el.innerHTML='<div class="phead"><select class="pbook" aria-label="Book on this side"></select><span class="pwhere"></span><a class="popen" target="_blank" rel="noopener" title="Open this place in the book">Open ↗</a></div>'+
      '<div class="pnote" hidden></div><div class="pscroll" tabindex="-1"><div class="col"><section class="chapter on"></section><nav class="pnav"></nav></div></div>';
    this.sel=$('.pbook',el); this.whereEl=$('.pwhere',el); this.open=$('.popen',el); this.note=$('.pnote',el);
    this.scroll=$('.pscroll',el); this.body=$('.chapter',el); this.nav=$('.pnav',el);
    this.sel.innerHTML=BOOKS.map(b=>'<option value="'+b.slug+'">'+esc(b.cite)+' — '+esc(b.title)+'</option>').join('');
  }
  Pane.prototype.show=function(ch){
    const P=this, B=P.B;
    if(P.ch===ch) return Promise.resolve();
    return part(B,ch).then(h=>{
      P.ch=ch; const c=B.chapters[B.chap[ch]], i=B.chap[ch];
      P.body.id=ch; P.body.innerHTML=h;
      P.body._pw=false; if(window.PaliWords) PaliWords.init('../').then(()=>{ if(P.ch===ch){ PaliWords.unlink(P.body); PaliWords.mark(P.body,B.slug); } });
      P.body.querySelectorAll('a[href="#home"]').forEach(a=>{ a.href='../'+B.slug+'/#home'; a.target='_blank'; });
      const prev=B.chapters[i-1], next=B.chapters[i+1];
      P.nav.innerHTML=(prev?'<button type="button" data-ch="'+prev.id+'">← '+esc(prev.title||prev.label)+'</button>':'<span></span>')+
                      (next?'<button type="button" data-ch="'+next.id+'">'+esc(next.title||next.label)+' →</button>':'');
      P.scroll.scrollTop=0;
    });
  };
  Pane.prototype.go=function(id,off,flash){
    const P=this, ch=chapterOf(P.B,id);
    if(!ch) return Promise.resolve(false);
    return P.show(ch).then(()=>{
      const el=id===ch?null:byId(P.body,id);
      P.lock++;
      if(el){ P.scroll.scrollTop+=el.getBoundingClientRect().top-P.scroll.getBoundingClientRect().top-(off||40);
        if(flash){ el.classList.remove('cflash'); void el.offsetWidth; el.classList.add('cflash'); } }
      else P.scroll.scrollTop=0;
      setTimeout(()=>{ P.lock--; },120);
      P.update(); return true;
    });
  };
  /* the topmost place on this side that lines up with something */
  Pane.prototype.top=function(){
    const P=this, B=P.B; if(!B) return null;
    const ci=B.cmp.chs?B.cmp.chs.indexOf(P.ch):-1;
    const line=P.scroll.getBoundingClientRect().top+70;
    let best=null, first=null;
    P.body.querySelectorAll('[id]').forEach(el=>{
      const i=B.mi[el.id]; if(i===undefined||B.cmp.c[i]!==ci) return;
      const t=el.getBoundingClientRect().top;
      if(t<=line){ if(!best||i>=best.i) best={i,el,off:t-P.scroll.getBoundingClientRect().top}; }
      else if(!first) first={i,el,off:t-P.scroll.getBoundingClientRect().top};
    });
    return best||first;
  };
  Pane.prototype.update=function(){
    const P=this, B=P.B, c=B.chapters[B.chap[P.ch]], m=P.top();
    const r=m?ref(B,m.el.id):'';
    P.whereEl.textContent=(c.label&&c.label!==c.title?c.label+' · ':'')+(c.title||'')+(r?' · '+r:'');
    P.whereEl.title=P.whereEl.textContent;
    P.open.href='../'+B.slug+'/#'+(m?m.el.id:P.ch);
    if(P===A) saveURL();
  };

  const A=new Pane($('#paneA'),'A'), Bp=new Pane($('#paneB'),'B');
  const other=P=>P===A?Bp:A;

  /* where the other side should be, for the place this side is at */
  function target(from,to){
    if(!from.B||!to.B) return null;
    const m=from.top(); const ps=from.B.cmp.to[to.B.slug];
    if(!ps||!ps.length) return null;
    const ci=from.B.cmp.chs.indexOf(from.ch);
    let k=-1;
    if(m){ let lo=0, hi=ps.length-1; while(lo<=hi){ const mid=(lo+hi)>>1; if(ps[mid][0]<=m.i){ k=mid; lo=mid+1; } else hi=mid-1; } }
    if(k<0||from.B.cmp.c[ps[k][0]]!==ci){
      /* nothing at or before this place in this part: the first place further on in it */
      const j=ps.findIndex(p=>from.B.cmp.c[p[0]]===ci&&(!m||p[0]>m.i));
      if(j<0) return null; k=j;
    }
    return {id:ps[k][1], off:m?Math.max(40,m.off):40};
  }
  function say(P,msg){ P.note.hidden=!msg; P.note.innerHTML=msg||''; }
  function follow(from){
    const to=other(from);
    if(!syncOn()||!to.B) return Promise.resolve();
    const t=target(from,to);
    if(!t){ say(to,'Nothing in <b>'+esc(BY[to.B.slug].cite)+'</b> is linked to this part of '+esc(BY[from.B.slug].cite)+'. It stays where it was.'); return Promise.resolve(); }
    say(to,'');
    return to.go(t.id,t.off);
  }
  const syncOn=()=>$('#sync').checked;

  /* scrolling one side moves the other */
  [A,Bp].forEach(P=>{
    let t=null;
    P.scroll.addEventListener('scroll',()=>{
      if(P.lock||!P.B) return;
      clearTimeout(t); t=setTimeout(()=>{ P.update(); if(!narrow()) follow(P); },90);
    },{passive:true});
    P.nav.addEventListener('click',e=>{ const b=e.target.closest('button[data-ch]'); if(!b) return; P.go(b.dataset.ch).then(()=>{ if(!narrow()) follow(P); }); });
    P.sel.addEventListener('change',()=>setBook(P,P.sel.value));
    /* links in the text: to this book, to the book on the other side, or to a third book (it takes the other side) */
    P.body.addEventListener('click',e=>{
      const a=e.target.closest('a[href]'); if(!a) return;
      const h=a.getAttribute('href'); let m;
      if(h.startsWith('#')){ e.preventDefault(); const id=decodeURIComponent(h.slice(1)); if(chapterOf(P.B,id)) P.go(id,40,true).then(()=>{ if(!narrow()) follow(P); }); return; }
      if((m=h.match(/^\.\.\/([a-z]+)\/#(.+)$/)) && BY[m[1]]){
        e.preventDefault(); const slug=m[1], id=decodeURIComponent(m[2]);
        if(slug===P.B.slug){ P.go(id,40,true); return; }
        const O=other(P);
        const go=()=>O.go(id,40,true).then(()=>{ say(O,''); if(narrow()) showTab(O); });
        if(O.B&&O.B.slug===slug) go(); else loadInto(O,slug).then(go);
      }
    });
  });

  function loadInto(P,slug){
    P.el.classList.add('loading');
    return book(slug).then(B=>{ P.B=B; P.ch=null; P.sel.value=slug; P.el.dataset.book=slug; /* the book's own rules in reader.css ([data-book=…]) */ disableSame(); tabs(); P.el.classList.remove('loading'); });
  }
  function disableSame(){ [A,Bp].forEach(P=>{ const o=other(P); [...P.sel.options].forEach(op=>{ op.disabled=!!(o.B&&op.value===o.B.slug); }); }); }
  function setBook(P,slug){
    const O=other(P);
    return loadInto(P,slug).then(()=>{
      const t=O.B?target(O,P):null;
      if(t){ say(P,''); return P.go(t.id,t.off,true); }
      say(P,O.B?'Nothing in <b>'+esc(BY[slug].cite)+'</b> is linked to this part of '+esc(BY[O.B.slug].cite)+', so it opens at its beginning.':'');
      return P.go(firstPart(P.B));
    });
  }
  function firstPart(B){ /* the first part with something that lines up, else the first part */
    const c=B.cmp.chs&&B.cmp.chs[0]; return c||B.chapters[0].id;
  }

  /* swap the sides, each book keeping its place */
  $('#swap').addEventListener('click',()=>{
    const ma=A.top(), mb=Bp.top(), sa=A.B.slug, sb=Bp.B.slug;
    const ida=ma?ma.el.id:A.ch, idb=mb?mb.el.id:Bp.ch;
    A.B=null; Bp.B=null;
    Promise.all([loadInto(A,sb),loadInto(Bp,sa)]).then(()=>{ A.ch=null; Bp.ch=null; return Promise.all([A.go(idb),Bp.go(ida)]); }).then(()=>{ say(A,''); say(Bp,''); if(narrow()) showTab(cur===A?Bp:A,true); });
  });
  $('#sync').addEventListener('change',()=>{ if(syncOn()&&!narrow()) follow(A); });

  /* on a phone: one side at a time, the tabs switch, and the side shown is moved to the place of the other */
  let cur=A;
  function tabs(){
    $('#ptabs').innerHTML=[A,Bp].map(P=>'<button type="button" data-p="'+P.name+'" aria-pressed="'+(P===cur)+'">'+esc(P.B?BY[P.B.slug].cite:'…')+'</button>').join('<span aria-hidden="true">⇄</span>');
  }
  function showTab(P,noFollow){
    const from=cur; const t=(!noFollow&&P!==from&&syncOn())?target(from,P):null;
    cur=P; A.el.classList.toggle('show',P===A); Bp.el.classList.toggle('show',P===Bp); tabs();
    if(t){ say(P,''); P.go(t.id,t.off); }
    else if(!noFollow&&P!==from&&syncOn()&&from.B&&P.B) say(P,'Nothing in <b>'+esc(BY[P.B.slug].cite)+'</b> is linked to this part of '+esc(BY[from.B.slug].cite)+'.');
  }
  $('#ptabs').addEventListener('click',e=>{ const b=e.target.closest('button[data-p]'); if(!b) return; showTab(b.dataset.p==='A'?A:Bp); });

  /* the address: ?a=pali&b=sammoha&at=p58 (at = the place on the left) */
  let urlT=null;
  function saveURL(){ clearTimeout(urlT); urlT=setTimeout(()=>{
    if(!A.B||!Bp.B) return; const m=A.top();
    const p=new URLSearchParams({a:A.B.slug,b:Bp.B.slug,at:m?m.el.id:A.ch});
    history.replaceState(null,'','?'+p);
    document.title=BY[A.B.slug].cite+' ⇄ '+BY[Bp.B.slug].cite+' · '+document.title.split(' · ').slice(-1)[0];
  },300); }

  /* start */
  const q=new URLSearchParams(location.search);
  let a=BY[q.get('a')]?q.get('a'):'pali', b=BY[q.get('b')]?q.get('b'):BY[a].partner;
  if(b===a) b=BY[a].partner;
  const at=q.get('at');
  A.el.classList.add('show');
  Promise.all([loadInto(A,a),loadInto(Bp,b)]).then(()=>A.go(at&&chapterOf(A.B,at)?at:firstPart(A.B),40,!!at)).then(()=>{
    const t=target(A,Bp);
    if(t) return Bp.go(t.id,t.off);
    say(Bp,'Nothing in <b>'+esc(BY[b].cite)+'</b> is linked to this part of '+esc(BY[a].cite)+', so it opens at its beginning.');
    return Bp.go(firstPart(Bp.B));
  }).catch(err=>{ A.note.hidden=false; A.note.textContent='This page could not be loaded ('+err.message+'). Try reloading it.'; });
})();
