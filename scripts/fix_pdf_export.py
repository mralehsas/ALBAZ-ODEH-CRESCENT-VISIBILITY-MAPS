from pathlib import Path
import re

path = Path("index.html")
s = path.read_text(encoding="utf-8")

# Repair the duplicated/corrupted block introduced while preparing the public build.
marker = "function getEmbeddedFontFaceCSS(){"
positions = [m.start() for m in re.finditer(re.escape(marker), s)]
if len(positions) >= 2:
    s = s[:positions[0]] + s[positions[1]:]
elif len(positions) == 0:
    raise SystemExit("getEmbeddedFontFaceCSS marker not found")

# The public build does not redistribute the embedded commercial font.
font_start = s.find(marker)
font_end = s.find("function getSiteInfo(){", font_start)
if font_start < 0 or font_end < 0:
    raise SystemExit("font helper boundaries not found")
s = s[:font_start] + 'function getEmbeddedFontFaceCSS(){\n  return "";\n}\n\n' + s[font_end:]

pdf_start = s.find("function openPDFReport(){")
pdf_end = s.find("function escapeHTML", pdf_start)
if pdf_start < 0 or pdf_end < 0:
    raise SystemExit("PDF function boundaries not found")

new_pdf = '''function openPDFReport(){
  // Open synchronously so GitHub Pages browsers do not block it as a delayed popup.
  const w = window.open('', '_blank');
  if(!w){
    alert('المتصفح منع فتح نافذة التقرير. اسمح بالنوافذ المنبثقة لهذا الموقع ثم أعد المحاولة.');
    return;
  }

  w.document.open();
  w.document.write(`<!doctype html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><title>إعداد تقرير PDF</title></head><body style="font-family:Tahoma,Arial,sans-serif;background:#f7f9fc;color:#0f2742;display:grid;place-items:center;min-height:100vh;margin:0"><div style="text-align:center"><h2>جارٍ إعداد تقرير PDF…</h2><p>يرجى الانتظار لحظات.</p></div></body></html>`);
  w.document.close();

  try{
    try{ runAuditCities(); }catch(e){ console.warn(e); }
    const htmlReport = makeReportHTML(false);

    w.document.open();
    w.document.write(htmlReport);
    w.document.close();

    let printStarted = false;

    const addPrintButton = () => {
      if(!w || w.closed || !w.document || !w.document.body) return;
      if(w.document.getElementById('manualPdfPrintBtn')) return;
      const btn = w.document.createElement('button');
      btn.id = 'manualPdfPrintBtn';
      btn.className = 'noPrint';
      btn.type = 'button';
      btn.textContent = 'طباعة / حفظ PDF';
      btn.style.cssText = 'position:fixed;top:14px;left:14px;z-index:9999;border:0;border-radius:10px;padding:11px 16px;background:#0f62a8;color:#fff;font:700 14px Tahoma,Arial,sans-serif;cursor:pointer;box-shadow:0 8px 24px rgba(0,0,0,.22)';
      btn.onclick = () => { w.focus(); w.print(); };
      w.document.body.prepend(btn);
    };

    const waitForReportAssets = async () => {
      if(printStarted || !w || w.closed) return;
      printStarted = true;
      addPrintButton();

      const images = Array.from(w.document.images || []);
      await Promise.all(images.map(img => {
        if(img.complete && img.naturalWidth > 0) return Promise.resolve();
        return new Promise(resolve => {
          let settled = false;
          const done = () => {
            if(settled) return;
            settled = true;
            resolve();
          };
          img.addEventListener('load', done, {once:true});
          img.addEventListener('error', done, {once:true});
          setTimeout(done, 4000);
        });
      }));

      if(w.document.fonts && w.document.fonts.ready){
        try{ await w.document.fonts.ready; }catch(e){}
      }

      setTimeout(() => {
        if(!w.closed){
          w.focus();
          w.print();
        }
      }, 350);
    };

    if(w.document.readyState === 'complete'){
      waitForReportAssets();
    }else{
      w.addEventListener('load', waitForReportAssets, {once:true});
      setTimeout(waitForReportAssets, 1200);
    }

    const st = document.getElementById('status');
    if(st) st.textContent = 'تم فتح تقرير PDF. اختر «حفظ بتنسيق PDF» من نافذة الطباعة.';
  }catch(err){
    console.error(err);
    if(w && !w.closed){
      w.document.open();
      w.document.write(`<p dir="rtl" style="font-family:Tahoma,Arial,sans-serif;padding:24px;color:#b42318">تعذر إنشاء تقرير PDF: ${escapeHTML(err.message || err)}</p>`);
      w.document.close();
    }
    alert('تعذر إنشاء تقرير PDF: ' + (err.message || err));
  }
}


'''

s = s[:pdf_start] + new_pdf + s[pdf_end:]
path.write_text(s, encoding="utf-8")
print("PDF export repaired")
