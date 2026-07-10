# دليل عرض Agentic SQL Dashboard

هذا الدليل مخصص للتحضير للمقابلة. السلايدات باللغة الإنجليزية، أما هذا الملف
فيعطيك طريقة العرض والجمل التي تشرح بها قراراتك بالعربي أو تحولها إلى إنجليزي.

## الفكرة الأساسية

لا تحاول إظهار أن المشروع كبير. قل إنك صممته ليكون صغيرًا وقابلًا للشرح:

> كل node لها مسؤولية واحدة، والـ state واضح، وأخطاء SQL لها مسار إصلاح محدود،
> بينما قرار العرض النهائي يعتمد على البيانات الفعلية.

## الأدوات

- PowerShell لتشغيل الـ API والواجهة.
- VS Code لفتح الملفات عند طلب شرح تفصيلي.
- المتصفح لعرض Streamlit.
- GitHub لعرض README وصورة القراف.
- OpenRouter موجود داخل `.env`، ولا تفتح هذا الملف أثناء مشاركة الشاشة.

لا تحتاج Postman أو LangSmith في العرض. المتصفح ونافذتا Terminal تكفيان.

## قبل المقابلة

```powershell
.\.venv\Scripts\Activate.ps1
python data\seed.py
uvicorn backend.main:app --reload
```

وفي Terminal ثانية:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend\app.py
```

تأكد من أن `http://127.0.0.1:8000/health` يعيد `status: ok`، ثم افتح
`http://127.0.0.1:8501`.

## ترتيب الديمو

ابدأ بالواجهة العاملة، ثم استخدم هذه الأسئلة بالترتيب:

| السؤال | العرض المتوقع | ماذا تشرح؟ |
| --- | --- | --- |
| What is the total revenue for completed orders? | KPI | صف واحد وقيمة رقمية واحدة |
| Show monthly revenue for completed orders. | Line | شهر/تاريخ مع رقم |
| What are the top 5 products by revenue? | Bar | فئة مع قيمة رقمية |
| List each product with its category and price. | Table | نتيجة تفصيلية متعددة الأعمدة |

## النص المقترح

### البداية

> هذا المشروع يحول سؤالًا طبيعيًا إلى SQL، يتحقق من الاستعلام، ينفذه بأمان،
> ثم يعرض النتيجة بالشكل المناسب. ركزت على وضوح الـ workflow بدل بناء واجهة
> كبيرة لأن هذا هو جوهر المهمة.

بالإنجليزية:

> I kept the UI intentionally minimal because the assignment prioritizes the
> agent workflow. The system generates structured SQL, validates it, executes it
> safely, and selects a display based on the actual result shape.

### عند ظهور KPI

> هذه النتيجة تحتوي قيمة رقمية واحدة، لذلك تظهر كـ KPI. القرار لا يعتمد على
> اسم السؤال فقط؛ الـ backend يفحص الصفوف والأعمدة بعد تنفيذ SQL.

### عند ظهور Line chart

> هنا لدينا عمود شهر وعمود إيراد، لذلك النتيجة time series وتظهر كـ line chart.
> الـ LLM يقترح hint، لكن node اسمها `decide_display` تتحقق من شكل البيانات.

### عند ظهور Bar chart

> هنا نقارن فئات، وهي المنتجات، بقيمة رقمية هي الإيراد. لذلك bar chart أوضح
> من table لهذه النتيجة.

### عند ظهور Table

> هذه نتيجة تفصيلية فيها أكثر من عمود، لذلك table يحافظ على كل المعلومات بدل
> تحويلها إلى رسم يخفي بعض الحقول.

### عند شرح الإصلاح

> إذا فشل validation أو execution، ينتقل الـ graph إلى `repair_sql` ثم يعود إلى
> `validate_sql`. حددت المحاولات باثنتين حتى لا يكون عندي loop غير منتهٍ أو تكلفة
> API غير محدودة.

## الملفات التي تفتحها عند السؤال

1. `backend/graph.py` لشرح nodes والـ conditional routes.
2. `backend/state.py` لشرح الحقول المشتركة وعدد المحاولات.
3. `backend/validators.py` لشرح SELECT-only وLIMIT.
4. `backend/db.py` لشرح read-only وschema.
5. `backend/display.py` لشرح KPI وline وbar وtable.
6. `README.md` لشرح التشغيل والقرارات.

لا تفتح كل الملفات من البداية. افتح الملف المرتبط بالسؤال فقط.

## إذا فشل الاتصال

قل:

> أخطاء SQL قابلة للإصلاح داخل graph، أما أخطاء OpenRouter أو الإعدادات فليست
> أخطاء SQL، لذلك يعالجها FastAPI عند حدود الخدمة ويرجع رسالة واضحة للمستخدم.

ثم تحقق من `/health` ومن تشغيل الـ backend، ولا تعرض قيمة المفتاح.
