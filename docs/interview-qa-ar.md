# أسئلة المقابلة المتوقعة وإجاباتها

## المعمارية

### لماذا LangGraph وليس chain عادية؟

لأن عندي state مشتركة ومسارات شرطية وrepair loop. الـ chain العادية تناسب
تدفقًا ثابتًا، أما LangGraph فيجعل النجاح والفشل والإصلاح واضحين وقابلين للاختبار.

### هل هذا Agentic فعلًا؟

نعم، لكنه agent محدود ومضبوط. النموذج يولد ويصلح SQL، والـ graph يقرر هل ينفذ،
أو يصلح، أو يختار العرض، أو ينهي العملية بفشل واضح.

### لماذا قسمت الـ graph إلى nodes كثيرة؟

لأن كل node لها مسؤولية واحدة: schema، generation، validation، execution، repair،
display، وsummary. هذا يقلل الترابط ويسهل معرفة مكان الخطأ.

### كيف تتحرك الـ state؟

تبدأ بـ `question` و`attempts`. بعدها يضاف `schema`، ثم `sql` و`display_hint`،
ثم `rows` و`columns`، وأخيرًا `display` و`answer`. كل node ترجع الحقول التي
غيرتها فقط، وLangGraph يدمجها مع الحالة الحالية.

### لماذا TypedDict؟

لأن الـ state هنا data contract بسيط ولا يحتاج behavior أو lifecycle مستقل. لذلك
`TypedDict` أوضح وأخف من class كبيرة.

### لماذا تحميل schema في كل سؤال؟

لأن schema جزء من سياق الـ agent وأردت أن يبقى ظاهرًا داخل graph. في الإنتاج
سأستخدم cache مع invalidation عند migrations لتقليل القراءة المتكررة.

### لماذا لا يوجد memory؟

كل سؤال مستقل في هذا الـ assignment. إضافة memory قد تجعل سؤالًا سابقًا يؤثر على
SQL جديد، وتضيف تعقيدًا لا تحتاجه المهمة.

## SQL والأمان

### لماذا validation قبل التنفيذ؟

لأن مخرجات الـ LLM احتمالية. الـ validator يسمح بـ SELECT واحد، يمنع كلمات الكتابة،
ويضيف LIMIT قبل وصول الاستعلام إلى قاعدة البيانات.

### لماذا validator مع read-only معًا؟

لأنهما طبقتان مختلفتان. الـ validator يعطي policy واضحة ورسالة مفهومة، و`mode=ro`
يجعل SQLite نفسها ترفض الكتابة حتى لو مر شيء من الطبقة الأولى بالخطأ.

### لماذا LIMIT 100؟

حتى لا يعيد استعلام تفصيلي عددًا ضخمًا من الصفوف ويؤثر على API والواجهة. هو حماية
لحجم النتيجة، وليس بديلًا عن query timeout في الإنتاج.

### لماذا محاولتان فقط للإصلاح؟

لإثبات self-correction مع إبقاء latency وتكلفة API محدودة. وضعت الرقم في constant
واحد حتى يتطابق الكود مع README.

### ماذا يحدث إذا أعاد النموذج SQL خاطئًا؟

يضع `validate_sql` الخطأ في state. يرسل graph SQL والخطأ والـ schema إلى
`repair_sql`، ثم يعيد SQL المصحح إلى validation. بعد انتهاء المحاولتين يرجع `fail`.

### هل regex validator آمن للإنتاج؟

لا أدعي ذلك. هو guard مناسب لهذا demo مع read-only SQLite. في الإنتاج أضيف SQL
parser أو AST validation، database role للقراءة فقط، timeout، وallowlist للجداول.

## العرض والواجهة

### لماذا يعطي النموذج display hint؟

لأن النموذج يفهم intent المستخدم؛ كلمة compare قد تشير إلى bar وكلمة trend إلى
line. لكنه hint فقط وليس القرار النهائي.

### لماذا القرار النهائي بعد التنفيذ؟

لأن النموذج قبل التنفيذ لا يعرف عدد الصفوف أو نوع الأعمدة الحقيقي. بعد التنفيذ
أستطيع منع chart فارغ أو مضلل بقواعد deterministic.

### لماذا لا يقرر Streamlit نوع الرسم؟

لأن chart policy جزء من قرار الـ agent، وليس من طبقة العرض. Streamlit يستلم
`DisplaySpec` ويرسمه فقط، وهذا يمنع تكرار منطق الأعمال في الواجهة.

### هل المشروع يعتبر Dashboard؟

هو query-driven minimal dashboard، وليس BI dashboard ثابتًا. كل سؤال يغير العنصر
الرئيسي بين KPI وline وbar وtable، وهذا يحقق dynamic dashboard elements في المهمة.

### لماذا Streamlit؟

لأن الـ styling ليس أولوية. يوفر input وKPI وcharts وtable بكود قليل، وبالتالي
أركز وقتي على LangGraph وSQL safety.

### لماذا FastAPI؟

لأنه يعطي HTTP boundary typed بين الواجهة والـ graph، مع request validation وhealth
check وerror responses واضحة.

## النموذج والاختبارات

### لماذا OpenRouter؟

لأنه يوفر API متوافقًا مع OpenAI، فاستطعت إبقاء `ChatOpenAI` وعزل الإعدادات داخل
`llm.py`. الاختيار المعلن هو OpenAI GPT-4o-mini عبر OpenRouter.

### لماذا structured output؟

لأن graph يحتاج حقولًا ثابتة: `sql` و`explanation` و`display_hint`. Pydantic يمنع
parsing هشًا لنص أو JSON غير متوقع.

### لماذا summary node منفصلة؟

لأن توليد SQL وشرح النتيجة مسؤوليتان مختلفتان. إذا فشل التلخيص، تبقى rows وSQL
والـ dashboard متاحة، ويوجد fallback deterministic.

### كيف اختبرت المشروع؟

عندي اختبارات للـ validator، وقواعد العرض، وgraph happy path، ومسار repair. كما
اختبرت الأسئلة الأربعة عبر API الحقيقي وتأكدت من KPI وline وbar وtable.

### ماذا تطور في الإنتاج؟

Schema cache مع invalidation، query timeout، authentication، audit logs، evaluation
dataset، وtracing. أبقيتها خارج demo حتى تظل كل node سهلة الفهم.

### ما أكبر trade-off؟

اخترت explainability والبساطة على SQL expressiveness الكاملة. لذلك لا أدعم CTEs
في نسخة demo، لكن أعرف أن نسخة الإنتاج تحتاج parser أقوى وSQL dialect أوسع.

### هل استخدمت أدوات AI أثناء التطوير؟

الإجابة الصادقة:

> استخدمت التوثيق وأدوات AI للمراجعة واستكشاف البدائل، لكن أبقيت التنفيذ صغيرًا،
> وراجعت كل module، واختبرت السلوك، وأستطيع شرح سبب كل قرار وحدوده.
