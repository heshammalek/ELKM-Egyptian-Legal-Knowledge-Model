# 🚀 دليل التشغيل الكامل - ELKM Setup Guide

هذا الدليل يشرح كيفية إعداد وتشغيل مشروع **ELKM (Egyptian Legal Knowledge Model)** من الصفر، بدءاً من تجهيز البيئة، مروراً بتشغيل قاعدة البيانات وبناء الجراف المعرفي، وانتهاءً بإغلاق كل شيء بشكل سليم.

---

## 📋 المتطلبات الأساسية

قبل البدء، تأكد من توفر ما يلي على جهازك:

- **Python 3.10+**
- **Neo4j Desktop** (مع داتابيز جاهزة)
- **Git**

---

## الخطوة 1: تجهيز البيئة (Environment Setup)

افتح الـ Terminal (PowerShell أو CMD) وانتقل لمجلد المشروع:

```bash
cd ELKM-Egyptian-Legal-Knowledge-Model
```

أنشئ بيئة وهمية (Virtual Environment):

```bash
python -m venv venv
```

فعّل البيئة:

```bash
# على Windows
venv\Scripts\activate

# على Mac/Linux
source venv/bin/activate
```

ثبّت المكتبات المطلوبة:

```bash
pip install -r requirements.txt
```

---

## الخطوة 2: إعداد ملف `.env`

في جذر المشروع، أنشئ ملفاً باسم `.env` وضع فيه الإعدادات التالية (غيّر القيم حسب إعدادك المحلي):

```env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=egylaw
```

> ⚠️ **ملاحظة أمنية:** لا ترفع ملف `.env` إلى GitHub أبداً. تأكد من إضافته إلى `.gitignore`.

---

## الخطوة 3: تشغيل قاعدة البيانات (Neo4j)

1. افتح **Neo4j Desktop**.
2. اختر الداتابيز الخاصة بك.
3. اضغط على زر **Start** وانتظر حتى يتحول اللون إلى الأخضر وتظهر كلمة **RUNNING**.

للتأكد من أن الاتصال يعمل، شغّل الأمر التالي في الـ Terminal:

```bash
python -m scripts.utils.db
```

يجب أن تظهر لك الرسالة:

```text
✅ Neo4j connected successfully.
```

---

## الخطوة 4: التحقق من البيانات (Validation)

قبل بناء الجراف، تأكد من سلامة ملفات الـ JSON:

```bash
python scripts/validate.py
```

إذا ظهرت أخطاء، قم بإصلاحها أولاً (مثل حذف الملفات الفارغة أو تعديل `total_documents` في `documents_index.json`).

---

## الخطوة 5: بناء الجراف المعرفي (Graph Construction)

شغّل السكريبتات **بالترتيب التالي**:

### 1. تحميل الميتاداتا (الكيانات والمناصب)

```bash
python -m scripts.graph.import_metadata
```

### 2. تحميل المستندات والمواد

```bash
python -m scripts.graph.import_documents
```

### 3. تحميل العلاقات

```bash
python -m scripts.graph.import_relations
```

---

## الخطوة 6: التحقق من الجراف

افتح **Neo4j Browser** (من داخل Neo4j Desktop) وشغّل الاستعلامات التالية:

### عرض إحصائيات العقد (Nodes)

```cypher
MATCH (n) RETURN labels(n) AS Node_Type, count(n) AS Count;
```

يجب أن ترى عقداً من الأنواع التالية: `Document`, `Article`, `Entity`, `Position`.

### عرض عدد العلاقات (Relations)

```cypher
MATCH ()-[r:RELATION]->() RETURN count(r) AS Total_Relations;
```

---

## الخطوة 7: إغلاق كل شيء (Shutdown)

1. أغلق **Neo4j Browser** (المتصفح).
2. من **Neo4j Desktop**، اضغط **Stop** على الداتابيز.
3. أغلق **Neo4j Desktop**.
4. من الـ Terminal، اخرج من البيئة الوهمية:

```bash
deactivate
```

---

## ✅ ملاحظات مهمة

- **البيانات محفوظة:** عند إغلاق البرنامج، لا تُحذف البيانات. تبقى محفوظة على القرص حتى تقوم بتشغيل الداتابيز مرة أخرى.
- **إضافة مستندات جديدة:** ضع الملفات الجديدة في `corpus/normalized/`، ثم أعد تشغيل `import_documents` و `import_relations`.
- **استعلامات Cypher:** راجع ملف `scripts/queries_reference.cypher` للاطلاع على أمثلة إضافية للاستعلامات المفيدة.

---

## 📚 مراجع إضافية

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Python Neo4j Driver Documentation](https://neo4j.com/docs/python-manual/current/)
