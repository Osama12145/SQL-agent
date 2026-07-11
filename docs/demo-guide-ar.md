# دليل الديمو المحدث

هذا الدليل يطابق العرض الجديد سلايدًا بسلايد. السلايدات والنص المقروء بالإنجليزية
لأن المقابلة التقنية غالبًا ستكون بالإنجليزية، وتحت كل جزء ستجد الفكرة بالعربي.

## قبل المقابلة

شغّل الـAPI:

~~~powershell
cd C:\tmp\agentic_sql_dashboard
.\.venv\Scripts\python.exe data\seed.py
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --reload
~~~

وفي نافذة ثانية شغّل الواجهة:

~~~powershell
cd C:\tmp\agentic_sql_dashboard
.\.venv\Scripts\streamlit.exe run frontend\app.py
~~~

تأكد من http://127.0.0.1:8000/health ثم افتح http://127.0.0.1:8501.
لا تشارك الـTerminal ولا ملف .env أثناء العرض.

## تصحيح صغير مهم في سلايد 3

الجملة الحالية تقول إن الرسم تم توليده تلقائيًا من الـgraph وقت التشغيل. هذا غير
دقيق في المشروع الحالي: الرسم محفوظ بصيغة Mermaid/SVG بجانب الكود. استبدل subtitle
في سلايد 3 بهذه الجملة:

> The graph is defined in code; this diagram makes its nodes and routes easy to review.

هذا ليس تقليلًا من المشروع؛ بالعكس، هو جواب دقيق واحترافي إذا سألوا عن مصدر الرسم.

## ترتيب العرض

1. سلايدات 1 إلى 6: الفكرة والقرارات المعمارية، حوالي أربع دقائق.
2. سلايد 7 ثم الديمو الحي: حوالي دقيقتين.
3. سلايدات 8 إلى 10: التقنيات والحدود والخلاصة، حوالي دقيقتين.
4. اترك بقية الوقت للأسئلة.

## النص الذي تقوله

### سلايد 1: البداية

> Good morning. This is an Agentic SQL Dashboard built with LangGraph. A user
> asks a business question in natural language, the system generates safe SQL,
> executes it against a read-only SQLite database, and returns both an answer
> and a dashboard view that fits the result.

> I intentionally kept the interface small. For this assignment, the important
> part is making the agent workflow and its engineering decisions easy to see
> and explain.

المعنى: لا تدافع عن بساطة الواجهة، قدمها كقرار واعٍ لأن المهمة تقيم الـagent.

### سلايد 2: مسار السؤال إلى الجواب

> This slide shows the complete contract. The user asks a natural-language
> question. The LLM returns structured SQL, an explanation, and a display hint.
> The SQL is validated, row-limited, and executed through a read-only
> connection. Finally, the system returns a written answer and a display chosen
> from the actual rows.

> The UI is intentionally minimal because the engineering decisions are the
> product being evaluated here.

المعنى: هذه إجابة المتطلبات الخمسة في الإيميل، من السؤال إلى dashboard يتغير.

### سلايد 3: لماذا LangGraph

> I used LangGraph because this is not a single prompt followed by one database
> call. It has state and meaningful branches. Validation can fail, execution can
> fail, and both failures can be repaired before the workflow continues.

> Each node has one responsibility: load the schema, generate SQL, validate it,
> execute it, decide the display, and summarize the result. The conditional
> routes make the recovery path visible instead of hiding it inside one large
> function.

> The repair loop is bounded by two attempts. That demonstrates self-correction
> without allowing unlimited latency or API cost.

المعنى: ركز على شرطين مهمين: validation يفشل أو execution يفشل. كلاهما يذهب إلى
repair_sql ثم يعود للتحقق، لكن بحد أقصى محاولتين.

### سلايد 4: الـstate

> The shared state is deliberately small. It contains the user question and
> schema, the SQL work, the returned rows and display result, and two control
> fields: attempts and error.

> Each node reads only the fields it needs and returns only the fields it owns.
> LangGraph merges those partial updates, which makes the flow traceable and
> keeps hidden memory out of the design.

المعنى: لا تقل إن الـstate تخزن كل شيء. اذكر المجموعات الأربع: input، SQL work،
result، وcontrol flow.

### سلايد 5: الأمان

> LLM-generated SQL should never be trusted directly, so I used defense in
> depth. The first layer is readable application policy: one SELECT statement,
> blocked write keywords, and a LIMIT of 100 rows.

> The second layer is enforced by SQLite itself. The database is opened with
> read-only mode, so it cannot be modified even if the validator misses an edge
> case. EXPLAIN QUERY PLAN also lets execution planning errors enter the same
> controlled repair route.

المعنى: لا تقل إن regex يكفي للحماية. قل إن validator سياسة مفهومة، وmode=ro طبقة
مستقلة تفرضها قاعدة البيانات.

### سلايد 6: قرار نوع العرض

> The LLM suggests a display type because it understands intent. For example,
> compare suggests a bar chart, trend suggests a line chart, and total suggests
> a KPI.

> But the suggestion is not the final authority. After execution, the
> decide_display node checks the real result shape. One numeric value becomes a
> KPI, date plus number becomes a line chart, category plus number becomes a bar
> chart, and detailed rows become a table. The Streamlit frontend only renders
> that backend decision.

المعنى: هذه أقوى نقطة عندك. الـLLM يفهم النية، لكن البيانات الفعلية تمنع chart
مضلل أو فارغ.

### سلايد 7: الانتقال إلى الديمو

> The slides explain the decisions. I will now use these four questions to show
> that the dashboard changes its primary display from the returned data.

## الديمو الحي

استخدم الأسئلة نفسها الموجودة في سلايد 7.

### KPI

~~~text
What is the total revenue for completed orders?
~~~

> This returns one numeric value, so the backend selects a KPI. The frontend did
> not choose this from the words in the question; it received a display
> specification after the SQL result was inspected.

### Line

~~~text
Show monthly revenue for completed orders.
~~~

> This result has a month column and a numeric revenue column, so it becomes a
> line chart. This is where the actual result confirms the LLM's trend hint.

### Bar

~~~text
What are the top 5 products by revenue?
~~~

> Here the data compares product categories with a numeric revenue value, so a
> bar chart is the most useful view. I will open Generated SQL once to show that
> the executed query is visible for transparency and debugging.

### Table

~~~text
List each product with its category and price.
~~~

> This is a detailed multi-column result. A table preserves the useful detail,
> whereas a chart would hide it.

لا تعمل error متعمد في الديمو. قل بدل ذلك:

> If validation or execution failed, the graph would route through repair_sql,
> return to validation, and stop with a clear failure after two repair attempts.

### سلايد 8: التقنية

> Each technology was selected for the evaluation scope. FastAPI creates a small
> typed boundary between the UI and graph. SQLite keeps the demo self-contained.
> Streamlit provides input, KPIs, charts, and tables without a large frontend.
> OpenRouter is OpenAI-compatible, so provider settings stay isolated in one
> module while the project retains the standard ChatOpenAI client.

### سلايد 9: الحدود الصادقة

> This project is deliberately small, not presented as production-complete. The
> current validator is a readable demo guard rather than a full SQL parser. For
> production, I would add database permissions, a proper parser, resource
> limits, authentication, auditing, schema caching, evaluations, and tracing.

> The important point is that these are explicit next steps, not hidden gaps in
> the current design.

### سلايد 10: الخلاصة

> To summarize: the LLM proposes structured SQL and a display hint, while
> LangGraph controls validation, repair, execution, and the final data-driven
> display decision. I kept every current node small enough to explain, test, and
> improve independently.

## عند سؤالهم عن الكود

لا تفتح كل المشروع. افتح الملف المطابق للسؤال:

1. backend/graph.py للـnodes والـconditional routes.
2. backend/state.py للـstate وعدد المحاولات.
3. backend/validators.py لسياسة SELECT-only وLIMIT.
4. backend/db.py لـread-only وschema.
5. backend/display.py لقواعد KPI وline وbar وtable.

## طريقة العرض العملية

- اعرض السلايدات 1 إلى 7، ثم انتقل للمتصفح بـ Alt + Tab.
- بعد الديمو ارجع للسلايد 8 وأكمل إلى 10.
- في مقابلة عن بعد شارك نافذة PowerPoint أو المتصفح، وليس كامل سطح المكتب.
- افتح Generated SQL مرة واحدة فقط.
- إذا فشل OpenRouter، لا تتوقف لمحاولة إصلاحه أمامهم؛ وضح أن أخطاء المزود مختلفة
  عن SQL errors وأن FastAPI يرجع رسالة واضحة.
