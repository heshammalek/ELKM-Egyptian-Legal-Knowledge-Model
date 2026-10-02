#!/usr/bin/env python3
"""
validate.py — فحص سلامة ملفات الميتا لمنع التكرار

يُشغَّل يدوياً أو تلقائياً (pre-commit hook).

الاستخدام:
    python scripts/validate.py
    python scripts/validate.py --verbose
    python scripts/validate.py --path corpus/metadata

الإرجاع:
    exit 0 — كل شيء سليم
    exit 1 — يوجد خطأ (تفاصيل تُطبع في stderr)
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter


# ============================================================================
# الأدوات المساعدة
# ============================================================================

class Colors:
    """ألوان للطباعة في الطرفية"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def log_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}", file=sys.stderr)


def log_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def log_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def log_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def load_json(path):
    """تحميل ملف JSON مع معالجة الأخطاء"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        log_error(f"JSON غير صالح في {path}: {e}")
        return None
    except FileNotFoundError:
        log_error(f"الملف غير موجود: {path}")
        return None


# ============================================================================
# الفحوصات
# ============================================================================

class Validator:
    def __init__(self, base_path, verbose=False):
        self.base_path = Path(base_path)
        self.verbose = verbose
        self.errors = []
        self.warnings = []
        self.stats = {}

    def add_error(self, msg):
        self.errors.append(msg)
        log_error(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)
        if self.verbose:
            log_warning(msg)


    # ------------------------------------------------------------------------
    # 1. فحص الوثائق (Documents)
    # ------------------------------------------------------------------------

    def validate_documents(self):
        log_info("فحص الوثائق (documents) ...")

        master_path = self.base_path / "documents_index.json"
        master = load_json(master_path)
        if not master:
            return

        all_doc_ids = []
        by_type = master.get("indices", {})

        for doc_type, entry in by_type.items():
            index_path = Path(entry["path"])
            # لو المسار نسبي، نضمّه للـ base_path
            if not index_path.is_absolute():
                # نحاول نجد الملف من مواقع مختلفة
                candidates = [
                    index_path,
                    self.base_path / index_path,
                    self.base_path.parent / index_path,
                ]
                index_path = next((c for c in candidates if c.exists()), None)
                if not index_path:
                    self.add_warning(f"ملف الفهرس غير موجود: {entry['path']}")
                    continue

            index_data = load_json(index_path)
            if not index_data:
                continue

            docs = index_data.get("documents", [])
            declared_count = index_data.get("count", 0)

            # فحص count
            if declared_count != len(docs):
                self.add_error(
                    f"عدم تطابق count في {index_path.name}: "
                    f"مُعلن={declared_count}, فعلي={len(docs)}"
                )

            # فحص تكرار doc_id داخل نفس الملف
            ids = [d.get("doc_id") for d in docs if d.get("doc_id")]
            duplicates = [i for i, c in Counter(ids).items() if c > 1]
            if duplicates:
                self.add_error(
                    f"تكرار doc_id في {index_path.name}: {duplicates}"
                )

            # فحص توافق doc_type
            for d in docs:
                if d.get("doc_type") != doc_type:
                    self.add_warning(
                        f"عدم توافق doc_type في {d.get('doc_id')}: "
                        f"مُعلن={doc_type}, فعلي={d.get('doc_type')}"
                    )

            all_doc_ids.extend(ids)
            self.stats[f"docs_{doc_type}"] = len(docs)

        # فحص تكرار doc_id عبر كل الأنواع
        cross_duplicates = [i for i, c in Counter(all_doc_ids).items() if c > 1]
        if cross_duplicates:
            self.add_error(f"تكرار doc_id عبر الأنواع: {cross_duplicates}")

        # فحص total_documents
        declared_total = master.get("total_documents", 0)
        if declared_total != len(all_doc_ids):
            self.add_error(
                f"total_documents في master لا يطابق المجموع: "
                f"مُعلن={declared_total}, فعلي={len(all_doc_ids)}"
            )

        self.stats["total_docs"] = len(all_doc_ids)
        log_success(f"وثائق: {len(all_doc_ids)}")


    # ------------------------------------------------------------------------
    # 2. فحص العلاقات (Relations)
    # ------------------------------------------------------------------------

    def validate_relations(self):
        log_info("فحص العلاقات (relations) ...")

        relations_dir = self.base_path / "relations" / "by_document"
        if not relations_dir.exists():
            self.add_warning(f"مجلد العلاقات غير موجود: {relations_dir}")
            return

        seen_instance_ids = set()
        count = 0

        for rel_file in relations_dir.glob("*.json"):
            rel = load_json(rel_file)
            if not rel:
                continue

            count += 1
            iid = rel.get("instance_id")

            # فحص 1: وجود instance_id
            if not iid:
                self.add_error(f"instance_id مفقود في {rel_file.name}")
                continue

            # فحص 2: تكرار instance_id
            if iid in seen_instance_ids:
                self.add_error(f"تكرار instance_id: {iid}")
            seen_instance_ids.add(iid)

            # فحص 3: تطابق اسم الملف مع instance_id
            if rel_file.stem != iid:
                self.add_error(
                    f"عدم تطابق اسم الملف مع instance_id: "
                    f"اسم={rel_file.stem}, معرف={iid}"
                )

            # فحص 4: وجود الحقول الإلزامية
            required = ["type_id", "type_name", "category_id", "source", "target"]
            for field in required:
                if field not in rel:
                    self.add_error(f"{field} مفقود في {rel_file.name}")

        self.stats["total_relations"] = count
        log_success(f"علاقات: {count}")


    # ------------------------------------------------------------------------
    # 3. فحص الكيانات (Entities)
    # ------------------------------------------------------------------------

    def validate_entities(self):
        log_info("فحص الكيانات (entities) ...")

        entities_path = self.base_path / "entities.json"
        data = load_json(entities_path)
        if not data:
            return

        entities = data.get("entities", [])
        ids = [e.get("entity_id") for e in entities if e.get("entity_id")]

        duplicates = [i for i, c in Counter(ids).items() if c > 1]
        if duplicates:
            self.add_error(f"تكرار entity_id: {duplicates}")

        # فحص وجود name_ar
        for e in entities:
            if not e.get("name_ar"):
                self.add_warning(f"name_ar مفقود في {e.get('entity_id')}")

        self.stats["total_entities"] = len(entities)
        log_success(f"كيانات: {len(entities)}")


    # ------------------------------------------------------------------------
    # 4. فحص المناصب (Positions)
    # ------------------------------------------------------------------------

    def validate_positions(self):
        log_info("فحص المناصب (positions) ...")

        positions_path = self.base_path / "positions.json"
        data = load_json(positions_path)
        if not data:
            return

        positions = data.get("positions", [])
        ids = [p.get("position_id") for p in positions if p.get("position_id")]

        duplicates = [i for i, c in Counter(ids).items() if c > 1]
        if duplicates:
            self.add_error(f"تكرار position_id: {duplicates}")

        self.stats["total_positions"] = len(positions)
        log_success(f"مناصب: {len(positions)}")


    # ------------------------------------------------------------------------
    # 5. فحص العلاقات المتقاطعة (Cross-references)
    # ------------------------------------------------------------------------

    def validate_cross_references(self):
        log_info("فحص المراجع المتقاطعة (cross-references) ...")

        # تحميل كل entity_ids
        entities_data = load_json(self.base_path / "entities.json")
        entity_ids = set()
        if entities_data:
            entity_ids = {e["entity_id"] for e in entities_data.get("entities", [])}

        # تحميل كل position_ids
        positions_data = load_json(self.base_path / "positions.json")
        position_ids = set()
        if positions_data:
            position_ids = {p["position_id"] for p in positions_data.get("positions", [])}

        # فحص المراجع في ملفات العلاقات
        relations_dir = self.base_path / "relations" / "by_document"
        if relations_dir.exists():
            for rel_file in relations_dir.glob("*.json"):
                rel = load_json(rel_file)
                if not rel:
                    continue

                target = rel.get("target", {})

                # فحص entity_id
                eid = target.get("entity_id")
                if eid and eid not in entity_ids:
                    self.add_warning(
                        f"entity_id غير موجود في entities.json: {eid} "
                        f"(في {rel_file.name})"
                    )

                # فحص position_id
                pid = target.get("position_id")
                if pid and pid not in position_ids:
                    self.add_warning(
                        f"position_id غير موجود في positions.json: {pid} "
                        f"(في {rel_file.name})"
                    )

        log_success("انتهى فحص المراجع المتقاطعة")


    # ------------------------------------------------------------------------
    # التشغيل الكامل
    # ------------------------------------------------------------------------

    def run_all(self):
        print(f"\n{Colors.BOLD}🔍 بدء فحص سلامة الميتا{Colors.RESET}")
        print(f"   المسار: {self.base_path}\n")

        self.validate_documents()
        self.validate_relations()
        self.validate_entities()
        self.validate_positions()
        self.validate_cross_references()

        print(f"\n{Colors.BOLD}📊 الملخص{Colors.RESET}")
        for key, value in self.stats.items():
            print(f"   {key}: {value}")

        print()

        if self.errors:
            print(f"{Colors.RED}{Colors.BOLD}❌ فشل الفحص: {len(self.errors)} خطأ{Colors.RESET}")
            return 1

        if self.warnings:
            print(f"{Colors.YELLOW}⚠️  تحذيرات: {len(self.warnings)}{Colors.RESET}")

        print(f"{Colors.GREEN}{Colors.BOLD}✅ كل شيء سليم{Colors.RESET}")
        return 0


# ============================================================================
# نقطة الدخول
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="فحص سلامة ملفات الميتا")
    parser.add_argument(
        "--path",
        default="corpus/metadata",
        help="مسار مجلد الميتا (افتراضي: corpus/metadata)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="طباعة كل التحذيرات"
    )
    args = parser.parse_args()

    validator = Validator(args.path, verbose=args.verbose)
    return validator.run_all()


if __name__ == "__main__":
    sys.exit(main())
