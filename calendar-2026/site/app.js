const $ = (s)=>document.querySelector(s);
const grid = $("#grid");
const modal = $("#modal");
const pdfFrame = $("#pdfFrame");
const selectedTitle = $("#selectedTitle");
const selectedPrice = $("#selectedPrice");
const previewBtn = $("#previewBtn");

const SKUS = [
  { id:"13_core",   title:"13-Month · Core",   price:"19", tags:["13-month","core","seasonal"], preview:"previews/13-core-preview.pdf", file:"assets/Calendar_2026_13_core.pdf" },
  { id:"13_deluxe", title:"13-Month · Deluxe", price:"24", tags:["13-month","deluxe","white gold black silver"], preview:"previews/13-deluxe-preview.pdf", file:"assets/Calendar_2026_13_deluxe.pdf" },
  { id:"13_neon",   title:"13-Month · Color Pop", price:"19", tags:["13-month","neon","color pop"], preview:"previews/13-neon-preview.pdf", file:"assets/Calendar_2026_13_neon.pdf" },
  { id:"12_core",   title:"12-Month · Core",   price:"15", tags:["12-month","core","gregorian"], preview:"previews/12-core-preview.pdf", file:"assets/Calendar_2026_12_core.pdf" },
  { id:"12_deluxe", title:"12-Month · Deluxe", price:"20", tags:["12-month","deluxe"], preview:"previews/12-deluxe-preview.pdf", file:"assets/Calendar_2026_12_deluxe.pdf" },
  { id:"12_neon",   title:"12-Month · Color Pop", price:"15", tags:["12-month","neon"], preview:"previews/12-neon-preview.pdf", file:"assets/Calendar_2026_12_neon.pdf" },
];

let picked = null;

function card(sku){
  const el = document.createElement("article");
  el.className = "card";
  el.dataset.sku = sku.id;
  el.dataset.group = sku.id.startsWith("13") ? "13" : "12";

  el.innerHTML = `
    <div class="card__top">
      <div class="card__title">${sku.title}</div>
      <div class="badges">
        ${sku.tags.slice(0,3).map(t=>`<span class="badge">${t}</span>`).join("")}
        <span class="badge">$${sku.price}</span>
      </div>
    </div>
    <iframe class="preview" loading="lazy" title="Preview ${sku.title}"></iframe>
    <div class="card__bot">
      <button class="btn btn--ghost" data-action="quick-preview">Preview</button>
      <div class="pick">
        <button class="btn" data-action="select">Select</button>
      </div>
    </div>
  `;

  // load preview or fallback
  const frame = el.querySelector("iframe");
  fetch(sku.preview,{method:"HEAD"}).then(r=>{
    frame.src = r.ok ? sku.preview : sku.file;
  }).catch(()=>{ frame.src = sku.file; });

  el.addEventListener("click",(ev)=>{
    const a = ev.target.closest("[data-action]");
    if(!a) return;
    if(a.dataset.action==="quick-preview"){ openPreview(sku); }
    if(a.dataset.action==="select"){ selectSku(sku); }
  });

  return el;
}

function render(items){
  grid.innerHTML="";
  items.forEach(s=>grid.appendChild(card(s)));
}

function selectSku(sku){
  picked = sku;
  selectedTitle.textContent = sku.title;
  selectedPrice.textContent = `$${sku.price}`;
  previewBtn.disabled = false;
  // highlight selected
  grid.querySelectorAll(".card").forEach(c=>{
    c.style.outline = c.dataset.sku===sku.id ? "2px solid #111" : "none";
    c.style.outlineOffset = "2px";
  });
}

function openPreview(sku){
  document.getElementById("modalTitle").textContent = `Preview · ${sku.title}`;
  // prefer preview; fallback to product
  fetch(sku.preview,{method:"HEAD"}).then(r=>{
    pdfFrame.src = r.ok ? sku.preview : sku.file;
    modal.showModal();
  }).catch(()=>{
    pdfFrame.src = sku.file;
    modal.showModal();
  });
}

$("#closeModal").addEventListener("click",()=>modal.close());
previewBtn.addEventListener("click",()=>{ if(picked) openPreview(picked); });

// search + filter
const search = $("#search");
const seg = document.querySelectorAll(".seg__btn");
let currentFilter = "all";

function applyFilters(){
  const q = search.value.trim().toLowerCase();
  const list = SKUS.filter(s=>{
    const passSeg = currentFilter==="all" ? true : s.id.startsWith(currentFilter);
    const hay = (s.title+" "+s.tags.join(" ")).toLowerCase();
    const passQ = q==="" || hay.includes(q);
    return passSeg && passQ;
  });
  render(list);
}
search.addEventListener("input", applyFilters);
seg.forEach(b=>{
  b.addEventListener("click",()=>{
    seg.forEach(x=>x.classList.remove("seg__btn--on"));
    b.classList.add("seg__btn--on");
    currentFilter = b.dataset.filter;
    applyFilters();
  });
});

// init
render(SKUS);
