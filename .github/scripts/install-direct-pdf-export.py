from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

replacement = r'''const PDF_HTML2CANVAS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
const PDF_JSPDF_URL = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';

function loadPDFScriptOnce(src, readyTest){
  return new Promise((resolve, reject) => {
    try{
      if(readyTest()){
        resolve();
        return;
      }
      let script = Array.from(document.scripts).find(s => s.src === src);
      if(!script){
        script = document.createElement('script');
        script.src = src;
        script.async = true;
        script.crossOrigin = 'anonymous';
        document.head.appendChild(script);
      }
      let finished = false;
      const done = () => {
        if(finished) return;
        finished = true;
        if(readyTest()) resolve();
        else reject(new Error('تعذر تحميل مكتبة إنشاء PDF.'));
      };
      const fail = () => {
        if(finished) return;
        finished = true;
        reject(new Error('تعذر الاتصال بمكتبة إنشاء PDF.'));
      };
      script.addEventListener('load', done, {once:true});
      script.addEventListener('error', fail, {once:true});
      setTimeout(() => {
        if(finished) return;
        if(readyTest()) done();
        else fail();
      }, 20000);
    }catch(err){
      reject(err);
    }
  });
}

async function ensurePDFLibraries(){
  await loadPDFScriptOnce(PDF_HTML2CANVAS_URL, () => typeof window.html2canvas === 'function');
  await loadPDFScriptOnce(PDF_JSPDF_URL, () => Boolean(window.jspdf && window.jspdf.jsPDF));
}

function waitForDocumentImages(doc, timeoutMs=8000){
  const images = Array.from(doc.images || []);
  return Promise.all(images.map(img => {
    if(img.complete) return Promise.resolve();
    return new Promise(resolve => {
      let settled = false;
      const done = () => {
        if(settled) return;
        settled = true;
        resolve();
      };
      img.addEventListener('load', done, {once:true});
      img.addEventListener('error', done, {once:true});
      setTimeout(done, timeoutMs);
    });
  }));
}

function createReportFrame(htmlReport){
  return new Promise((resolve, reject) => {
    const frame = document.createElement('iframe');
    frame.setAttribute('aria-hidden', 'true');
    frame.style.cssText = 'position:fixed;left:-12000px;top:0;width:1200px;height:1600px;border:0;opacity:0;pointer-events:none;background:#fff;';
    let settled = false;
    const cleanupFailure = err => {
      if(settled) return;
      settled = true;
      frame.remove();
      reject(err);
    };
    frame.addEventListener('load', () => {
      if(settled) return;
      settled = true;
      resolve(frame);
    }, {once:true});
    document.body.appendChild(frame);
    frame.srcdoc = htmlReport;
    setTimeout(() => cleanupFailure(new Error('انتهت مهلة إعداد تقرير PDF.')), 12000);
  });
}

async function printPDFReportFallback(htmlReport){
  const frame = await createReportFrame(htmlReport);
  try{
    const doc = frame.contentDocument;
    await waitForDocumentImages(doc, 5000);
    if(doc.fonts && doc.fonts.ready){
      try{ await doc.fonts.ready; }catch(e){}
    }
    frame.style.left = '0';
    frame.style.top = '0';
    frame.style.width = '1px';
    frame.style.height = '1px';
    frame.contentWindow.focus();
    frame.contentWindow.print();
  }finally{
    setTimeout(() => frame.remove(), 60000);
  }
}

async function buildAndDownloadPDF(htmlReport){
  await ensurePDFLibraries();
  const frame = await createReportFrame(htmlReport);
  try{
    const doc = frame.contentDocument;
    await waitForDocumentImages(doc);
    if(doc.fonts && doc.fonts.ready){
      try{ await doc.fonts.ready; }catch(e){}
    }
    const root = doc.body;
    const docEl = doc.documentElement;
    const captureWidth = Math.max(1000, root.scrollWidth, docEl.scrollWidth);
    const captureHeight = Math.max(root.scrollHeight, docEl.scrollHeight);
    const canvas = await window.html2canvas(root, {
      scale: 1.45,
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      logging: false,
      width: captureWidth,
      height: captureHeight,
      windowWidth: captureWidth,
      windowHeight: captureHeight,
      scrollX: 0,
      scrollY: 0
    });
    if(!canvas.width || !canvas.height){
      throw new Error('تعذر تحويل التقرير إلى صورة PDF.');
    }
    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF({orientation:'portrait', unit:'mm', format:'a4', compress:true});
    const pageWidthMm = pdf.internal.pageSize.getWidth();
    const pageHeightMm = pdf.internal.pageSize.getHeight();
    const pxPerMm = canvas.width / pageWidthMm;
    const pageHeightPx = Math.max(1, Math.floor(pageHeightMm * pxPerMm));
    let pageIndex = 0;
    for(let sourceY = 0; sourceY < canvas.height; sourceY += pageHeightPx){
      const sliceHeight = Math.min(pageHeightPx, canvas.height - sourceY);
      const pageCanvas = document.createElement('canvas');
      pageCanvas.width = canvas.width;
      pageCanvas.height = sliceHeight;
      const ctx = pageCanvas.getContext('2d', {alpha:false});
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height);
      ctx.drawImage(canvas, 0, sourceY, canvas.width, sliceHeight, 0, 0, canvas.width, sliceHeight);
      if(pageIndex > 0) pdf.addPage('a4', 'portrait');
      const imageHeightMm = sliceHeight / pxPerMm;
      pdf.addImage(pageCanvas.toDataURL('image/jpeg', 0.92), 'JPEG', 0, 0, pageWidthMm, imageHeightMm, undefined, 'FAST');
      pageIndex += 1;
    }
    const dateValue = (document.getElementById('dateInput')?.value || new Date().toISOString().slice(0,10)).replace(/[^0-9-]/g, '');
    pdf.save(`ALBAZ_ODEH_CRESCENT_REPORT_${dateValue}.pdf`);
  }finally{
    frame.remove();
  }
}

async function openPDFReport(){
  const button = document.getElementById('pdfReportBtn');
  const status = document.getElementById('status');
  const originalText = button ? button.textContent : '';
  if(button){
    button.disabled = true;
    button.textContent = 'جارٍ إنشاء PDF…';
  }
  if(status) status.textContent = 'جارٍ تجهيز ملف PDF للتحميل المباشر…';
  let htmlReport = '';
  try{
    try{ runAuditCities(); }catch(e){ console.warn(e); }
    htmlReport = makeReportHTML(false);
    await buildAndDownloadPDF(htmlReport);
    if(status) status.textContent = 'تم إنشاء ملف PDF وتحميله بنجاح.';
  }catch(err){
    console.error('PDF export failed:', err);
    if(status) status.textContent = 'تعذر التحميل المباشر؛ جارٍ فتح نافذة الطباعة الاحتياطية…';
    try{
      if(!htmlReport) htmlReport = makeReportHTML(false);
      await printPDFReportFallback(htmlReport);
      alert('تعذر إنشاء PDF مباشر. فُتحت نافذة الطباعة الاحتياطية؛ اختر «حفظ بتنسيق PDF».');
    }catch(fallbackErr){
      console.error('PDF fallback failed:', fallbackErr);
      alert('تعذر تصدير PDF: ' + (err?.message || err) + '\n\nتحقق من اتصال الإنترنت ثم أعد المحاولة.');
      if(status) status.textContent = 'تعذر تصدير PDF.';
    }
  }finally{
    if(button){
      button.disabled = false;
      button.textContent = originalText || 'تقرير PDF';
    }
  }
}
'''

pattern = re.compile(r"function openPDFReport\(\)\{[\s\S]*?\n\}\n\n\nfunction escapeHTML\(v\)\{")
match = pattern.search(text)
if not match:
    raise SystemExit('Could not locate openPDFReport block')
new_text = text[:match.start()] + replacement + "\n\nfunction escapeHTML(v){" + text[match.end():]
path.write_text(new_text, encoding='utf-8')
print('Installed direct PDF export')
