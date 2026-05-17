export function renderHtml(title: string, body: string): string {
  return `<!DOCTYPE html><html><head><meta charset="utf-8"/>
<style>
  :root { color-scheme: dark; }
  body { font: 13px -apple-system, "Segoe UI", system-ui, sans-serif;
         background: #14171c; color: #e7e9ee; margin: 12px; }
  h1 { font-size: 14px; font-weight: 600; margin: 0 0 12px;
       background: linear-gradient(90deg,#ff7a18,#af002d); -webkit-background-clip: text;
       -webkit-text-fill-color: transparent; }
  textarea, input { background:#1f242c; color:#e7e9ee; border:1px solid #2a313a;
                    border-radius:6px; padding:8px; font:inherit; }
  button { background:linear-gradient(90deg,#ff7a18,#af002d); color:#fff; border:0;
           border-radius:6px; padding:6px 14px; margin-top:8px; cursor:pointer; }
  table tr:nth-child(odd) td { background:#1a1e25; }
</style></head><body><h1>Surya AI · ${title}</h1>${body}</body></html>`;
}
