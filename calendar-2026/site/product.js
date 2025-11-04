const $ = (s)=>document.querySelector(s);

const previewMap = {
  "13_core":   "previews/13-core-preview.pdf",
  "13_deluxe": "previews/13-deluxe-preview.pdf",
  "13_neon":   "previews/13-neon-preview.pdf",
  "12_core":   "previews/12-core-preview.pdf",
  "12_deluxe": "previews/12-deluxe-preview.pdf",
  "12_neon":   "previews/12-neon-preview.pdf",
};

const productMap = {
  "13_core":   "assets/Calendar_2026_13_core.pdf",
  "13_deluxe": "assets/Calendar_2026_13_deluxe.pdf",
  "13_neon":   "assets/Calendar_2026_13_neon.pdf",
  "12_core":   "assets/Calendar_2026_12_core.pdf",
  "12_deluxe": "assets/Calendar_2026_12_deluxe.pdf",
  "12_neon":   "assets/Calendar_2026_12_neon.pdf",
};

function setFrameToSku(sku) {
  const probe = previewMap[sku];
  const fallback = productMap[sku];
  fetch(probe, { method: "HEAD" })
    .then(r => { $("#pdfFrame").src = r.ok ? probe : fallback; })
    .catch(() => { $("#pdfFrame").src = fallback; });
}

$("#openPreview").addEventListener("click", () => setFrameToSku($("#sku").value));

