// ==========================================
// ELKM Project - Cypher Queries Reference
// ==========================================

// 1. عرض إحصائيات الجراف (عدد كل نوع Node)
MATCH (n) 
RETURN labels(n) AS Node_Type, count(n) AS Count;
// الغرض: بيوريك إجمالي عدد المستندات، المواد، الكيانات، والمناصب اللي في الجراف.

// 2. عرض عدد العلاقات الإجمالي
MATCH ()-[r:RELATION]->() 
RETURN count(r) AS Total_Relations;
// الغرض: بيوريك عدد العلاقات اللي دخلت الجراف.

// 3. عرض المستندات والمواد التابعة لها (شكل شجرة)
MATCH p = (d:Document)-[:HAS_ARTICLE]->(a:Article)
RETURN p 
LIMIT 50;
// الغرض: بيعرض شكل الجراف للمستندات والمواد بتاعتها (دايرة كبيرة و حواليها دواير صغيرة).

// 4. عرض العلاقات بين المواد (عشان تشوف الأسهم)
MATCH (src:Article)-[r:RELATION]->(tgt)
RETURN src, r, tgt 
LIMIT 50;
// الغرض: بيعرض 50 علاقة بين المواد، ومكتوب على السهم نوع العلاقة (زي amendment).

// 5. عرض أنواع العلاقات وعددها
MATCH ()-[r:RELATION]->()
RETURN r.type_name AS Relation_Type, count(r) AS Count
ORDER BY Count DESC;
// الغرض: بيوريك إحصائيات لكل نوع علاقة (تعديل، إلغاء، إحالة، إلخ).

// 6. عينة من علاقات التعديل (amendment)
MATCH (src:Article)-[r:RELATION {type_name: 'amendment'}]->(tgt)
RETURN src.doc_id AS Source_Doc, src.article_number AS Source_Art, 
       tgt.doc_id AS Target_Doc, tgt.article_number AS Target_Art,
       r.reference_text AS Reference
LIMIT 10;
// الغرض: بيوريك عينة من القوانين اللي بتعدل قوانين تانية.

// 7. عينة من علاقات إنشاء الكيانات (establishes)
MATCH (src:Article)-[r:RELATION {type_name: 'establishes'}]->(tgt:Entity)
RETURN src.doc_id AS Source_Doc, tgt.name_ar AS Established_Entity, 
       r.reference_text AS Reference
LIMIT 10;
// الغرض: بيوريك المواد اللي بتعمل كيانات جديدة (زي الهيئات).

// 8. عينة من علاقات التخويل (empowers)
MATCH (src:Article)-[r:RELATION {type_name: 'empowers'}]->(tgt:Position)
RETURN src.doc_id AS Source_Doc, tgt.name_ar AS Empowered_Position, 
       r.reference_text AS Reference
LIMIT 10;
// الغرض: بيوريك المواد اللي بتدي صلاحيات لمناصب.

// 9. عرض الإحالات (referral) - عينة
MATCH (src:Article)-[r:RELATION {type_name: 'referral'}]->(tgt)
RETURN src.doc_id AS Source_Doc, src.article_number AS Source_Art, 
       tgt.doc_id AS Target_Doc, tgt.article_number AS Target_Art
LIMIT 10;
// الغرض: بيوريك المواد اللي بتحيل لمواد تانية.

// 10. مسح كل البيانات (استخدمه بحذر!)
MATCH (n) DETACH DELETE n;
// الغرض: بيمسح كل الـ Nodes والعلاقات عشان تبدأ من الأول.
