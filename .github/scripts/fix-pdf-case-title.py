from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

helper = r'''
function getCurrentCaseTitle(){
  let dateText = '';
  try{
    if(typeof formatCaseDateArabic === 'function'){
      dateText = String(formatCaseDateArabic() || '').trim();
    }
  }catch(e){}

  if(!dateText){
    const dateLabel = document.getElementById('dateLabel');
    const dateInput = document.getElementById('dateInput');
    dateText = String(
      (dateLabel && dateLabel.textContent && dateLabel.textContent.trim() !== '—')
        ? dateLabel.textContent
        : ((dateInput && dateInput.value) || '')
    ).trim();
  }

  const baseTitle = 'تقرير خريطة رؤية الهلال حسب معيار عودة';
  return dateText ? `${baseTitle} — ${dateText}` : baseTitle;
}
'''.strip()

if not re.search(r'function\s+getCurrentCaseTitle\s*\(', text):
    marker = 'function makeReportHTML(includeScript=false){'
    if marker not in text:
        raise SystemExit('Could not locate makeReportHTML')
    text = text.replace(marker, helper + '\n\n' + marker, 1)

text = text.replace(
    'const title = getCurrentCaseTitle();',
    'const title = escapeHTML(getCurrentCaseTitle());',
    1,
)

path.write_text(text, encoding='utf-8')
print('Added getCurrentCaseTitle and secured report title')
