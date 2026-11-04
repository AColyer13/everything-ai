// Copy buttons for code blocks
document.querySelectorAll('pre').forEach(pre=>{
  const b=document.createElement('button');b.className='copy';b.textContent='Copy';
  b.onclick=()=>{navigator.clipboard.writeText(pre.innerText.replace(/^Copy\n?/,'')).then(()=>{b.textContent='Copied';setTimeout(()=>b.textContent='Copy',1200)})};
  pre.appendChild(b);
});
// Table of contents highlight
const links=[...document.querySelectorAll('aside.toc a')];
if(links.length){
  const map=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));
  const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove('on'));const a=map.get(e.target.id);a&&a.classList.add('on')}})},{rootMargin:'-20% 0px -70% 0px'});
  document.querySelectorAll('main h2[id]').forEach(h=>io.observe(h));
}
// Site search (index built by build.py)
const input=document.getElementById('q'),box=document.getElementById('results');
if(input&&window.SEARCH_INDEX){
  input.addEventListener('input',()=>{
    const t=input.value.trim().toLowerCase();
    if(t.length<2){box.style.display='none';return}
    const words=t.split(/\s+/);
    const hits=window.SEARCH_INDEX.filter(e=>words.every(w=>(e.t+' '+e.x).toLowerCase().includes(w))).slice(0,12);
    box.innerHTML=hits.length?hits.map(h=>`<a href="${h.u}"><b>${h.t}</b><small>${h.p}</small></a>`).join(''):'<a>No matches</a>';
    box.style.display='block';
  });
  document.addEventListener('click',e=>{if(!e.target.closest('.search'))box.style.display='none'});
  document.addEventListener('keydown',e=>{if(e.key==='/'&&document.activeElement!==input){e.preventDefault();input.focus()}});
}
// Glossary filter
const gf=document.getElementById('gfilter');
if(gf){gf.addEventListener('input',()=>{const t=gf.value.toLowerCase();document.querySelectorAll('.gloss dt').forEach(dt=>{const dd=dt.nextElementSibling;const m=(dt.textContent+dd.textContent).toLowerCase().includes(t);dt.classList.toggle('hide',!m);dd.classList.toggle('hide',!m)})})}
