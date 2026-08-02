# خرائط عودة للهلال — ALBAZ Odeh Crescent Visibility Maps

برنامج فلكي عربي مستقل لبناء خرائط إمكانية رؤية الهلال وفق **معيار عودة**، مع أدوات للتحليل والتدقيق والتصدير. يعمل المشروع كصفحة HTML ثابتة، ولا يحتاج إلى خادم خلفي أو عملية بناء.

## الإصدار

**v9.6.3 — Final Android/Web Build**

## الخصائص الرئيسية

- خريطة عالمية لمناطق إمكانية رؤية الهلال.
- تصنيف مناطق الرؤية بألوان معيار عودة.
- المقارنة بين يوم الرصد واليوم التالي.
- حساب مؤشرات الرؤية، ومنها مكث القمر، الاستطالة، فرق الارتفاع، فرق السمت، وعرض الهلال.
- تدقيق المدن المرجعية وعواصم العالم.
- عرض الاقتران المركزي والسطحي وأوقات الغروب وغروب القمر.
- تصدير الخريطة والتقارير بصيغ PNG وHTML وPDF.
- واجهة عربية متجاوبة للحاسوب والهاتف.
- ملف واحد يعمل محليًا بعد تنزيل المستودع.

## المعادلة المعروضة في البرنامج

```text
V = ARCV - (-0.1018W³ + 0.7319W² - 6.3226W + 7.1651)
```

أفضل وقت للرصد في واجهة البرنامج محسوب بعد الغروب بمقدار **4/9 من مكث القمر**.

## التشغيل محليًا

يمكن فتح `index.html` مباشرة في متصفح حديث. ولتجربة سلوك مطابق للاستضافة، شغّل خادمًا محليًا من مجلد المشروع:

```bash
python -m http.server 8080
```

ثم افتح:

```text
http://localhost:8080
```

## النشر على GitHub Pages

المستودع يتضمن Workflow جاهزًا في:

```text
.github/workflows/pages.yml
```

بعد رفع الملفات إلى فرع `main`:

1. افتح **Settings** في المستودع.
2. اختر **Pages**.
3. من **Build and deployment** اختر المصدر **GitHub Actions**.
4. افتح تبويب **Actions** وتابع مهمة `Deploy Odeh Atlas to GitHub Pages`.
5. بعد نجاح المهمة سيظهر رابط الموقع في صفحة النشر.

## بنية المستودع

```text
.
├── index.html
├── assets/
│   └── icon.svg
├── .github/workflows/
│   ├── pages.yml
│   └── validate.yml
├── site.webmanifest
├── CITATION.cff
├── CHANGELOG.md
├── CONTRIBUTING.md
├── DEPLOYMENT.md
├── LICENSE.md
├── PRIVACY.md
├── SECURITY.md
├── .gitattributes
├── .gitignore
└── .nojekyll
```

## ملاحظة علمية

النتائج حسابية فلكية. الرؤية الفعلية قد تتأثر بالطقس، وصفاء الأفق، والرطوبة، والغبار، وخبرة الراصد، ووسيلة الرصد. لا تُعامل الخريطة منفردةً بوصفها إعلانًا شرعيًا لبداية الشهر.

## حقوق الخطوط

نسخة المستودع العامة لا تتضمن ملف خط تجاري أو بيانات خط مضمّنة. تعتمد الواجهة على خطوط النظام المتاحة في جهاز المستخدم.

## الإعداد

**الفيزيائي عمر الباز**  
رئيس مبرمجين أقدم  
عضو الاتحاد العربي لعلوم الفضاء والفلك

---

## English summary

A standalone Arabic web application for generating crescent-visibility maps using the Odeh criterion. It provides global mapping, city auditing, astronomical indicators, and PNG/HTML/PDF report export. The repository is a static site and includes an automated GitHub Pages workflow.
