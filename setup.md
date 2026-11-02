# 🚀 دليل التشغيل الكامل | Complete Setup Guide - ELKM

هذا الدليل يشرح كيفية إعداد وتشغيل مشروع **ELKM (Egyptian Legal Knowledge Model)** من الصفر، بدءاً من تجهيز البيئة، مروراً بتشغيل قاعدة البيانات وبناء الجراف المعرفي، وانتهاءً بإغلاق كل شيء بشكل سليم.

This guide explains how to set up and run the **ELKM (Egyptian Legal Knowledge Model)** project from scratch, starting with environment preparation, through starting the database and building the knowledge graph, and ending with shutting everything down properly.

---

## 📋 المتطلبات الأساسية | Prerequisites

قبل البدء، تأكد من توفر ما يلي على جهازك:

Before you begin, make sure the following are available on your machine:

- **Python 3.10+**
- **Neo4j Desktop** (مع داتابيز جاهزة | with a ready-made database)
- **Git**

---

## الخطوة 1: تجهيز البيئة | Step 1: Environment Setup

افتح الـ Terminal (PowerShell أو CMD) وانتقل لمجلد المشروع:

Open the Terminal (PowerShell or CMD) and navigate to the project folder:

```bash
cd ELKM-Egyptian-Legal-Knowledge-Model
```

أنشئ بيئة وهمية (Virtual Environment):

Create a virtual environment:

```bash
python -m venv venv
```

فعّل البيئة:

Activate the environment:

```bash
# على Windows | On Windows
venv\Scripts\activate

# على Mac/Linux | On Mac/Linux
source venv/bin/activate
```

ثبّت المكتبات المطلوبة:

Install the required libraries:

```bash
pip install -r requirements.txt
```

---

## الخطوة 2: إعداد ملف `.env` | Step 2: Configure the `.env` File

في جذر المشروع، أنشئ ملفاً باسم `.env` وضع فيه الإعدادات التالية (غيّر القيم حسب إعدادك المحلي):

In the project root, create a file named `.env` and put the following settings in it (change the values to match your local setup):

```env
NEO4J_URI=neo4j://127.0.0.1:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=egylaw
```

> ⚠️ **ملاحظة أمنية:** لا ترفع ملف `.env` إلى GitHub أبداً. تأكد من إضافته إلى `.gitignore`.
>
> ⚠️ **Security note:** Never push the `.env` file to GitHub. Make sure it is added to `.gitignore`.

---

## الخطوة 3: تشغيل قاعدة البيانات (Neo4j) | Step 3: Start the Database (Neo4j)

1. افتح **Neo4j Desktop**.
   Open **Neo4j Desktop**.
2. اختر الداتابيز الخاصة بك.
   Select your database.
3. اضغط على زر **Start** وانتظر حتى يتحول اللون إلى الأخضر وتظهر كلمة **RUNNING**.
   Click the **Start** button and wait until the color turns green and the word **RUNNING** appears.

للتأكد من أن الاتصال يعمل، شغّل الأمر التالي في الـ Terminal:

To confirm the connection works, run the following command in the Terminal:

```bash
python -m scripts.utils.db
```

يجب أن تظهر لك الرسالة:

You should see the message:

```text
✅ Neo4j connected successfully.
```

---

## الخطوة 4: التحقق من البيانات | Step 4: Data Validation

قبل بناء الجراف، تأكد من سلامة ملفات الـ JSON:

Before building the graph, verify the integrity of the JSON files:

```bash
python scripts/validate.py
```

إذا ظهرت أخطاء، قم بإصلاحها أولاً (مثل حذف الملفات الفارغة أو تعديل `total_documents` في `documents_index.json`).

If errors appear, fix them first (for example, delete empty files or correct `total_documents` in `documents_index.json`).

---

## الخطوة 5: بناء الجراف المعرفي | Step 5: Graph Construction

شغّل السكريبتات **بالترتيب التالي**:

Run the scripts **in the following order**:

### 1. تحميل الميتاداتا (الكيانات والمناصب) | Load the metadata (entities and positions)

```bash
python -m scripts.graph.import_metadata
```

### 2. تحميل المستندات والمواد | Load the documents and articles

```bash
python -m scripts.graph.import_documents
```

### 3. تحميل العلاقات | Load the relations

```bash
python -m scripts.graph.import_relations
```

---

## الخطوة 6: التحقق من الجراف | Step 6: Verify the Graph

افتح **Neo4j Browser** (من داخل Neo4j Desktop) وشغّل الاستعلامات التالية:

Open **Neo4j Browser** (from inside Neo4j Desktop) and run the following queries:

### عرض إحصائيات العقد (Nodes) | Show node statistics

```cypher
MATCH (n) RETURN labels(n) AS Node_Type, count(n) AS Count;
```

يجب أن ترى عقداً من الأنواع التالية: `Document`, `Article`, `Entity`, `Position`.

You should see nodes of the following types: `Document`, `Article`, `Entity`, `Position`.

### عرض عدد العلاقات (Relations) | Show the number of relations

```cypher
MATCH ()-[r:RELATION]->() RETURN count(r) AS Total_Relations;
```

---

## الخطوة 7: إغلاق كل شيء | Step 7: Shutdown

1. أغلق **Neo4j Browser** (المتصفح).
   Close **Neo4j Browser** (the browser).
2. من **Neo4j Desktop**، اضغط **Stop** على الداتابيز.
   From **Neo4j Desktop**, click **Stop** on the database.
3. أغلق **Neo4j Desktop**.
   Close **Neo4j Desktop**.
4. من الـ Terminal، اخرج من البيئة الوهمية:
   From the Terminal, exit the virtual environment:

```bash
deactivate
```

---

## ✅ ملاحظات مهمة | Important Notes

- **البيانات محفوظة:** عند إغلاق البرنامج، لا تُحذف البيانات. تبقى محفوظة على القرص حتى تقوم بتشغيل الداتابيز مرة أخرى.
  **Data is persisted:** When you close the program, the data is not deleted. It stays saved on disk until you start the database again.
- **إضافة مستندات جديدة:** ضع الملفات الجديدة في `corpus/normalized/`، ثم أعد تشغيل `import_documents` و `import_relations`.
  **Adding new documents:** Place the new files in `corpus/normalized/`, then re-run `import_documents` and `import_relations`.
- **استعلامات Cypher:** راجع ملف `scripts/queries_reference.cypher` للاطلاع على أمثلة إضافية للاستعلامات المفيدة.
  **Cypher queries:** See the `scripts/queries_reference.cypher` file for additional examples of useful queries.

---

## 📚 مراجع إضافية | Additional References

- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Python Neo4j Driver Documentation](https://neo4j.com/docs/python-manual/current/)
