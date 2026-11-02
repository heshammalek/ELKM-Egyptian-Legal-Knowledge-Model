import os
import subprocess
import sys

# إضافة مسار الجذر للنظام عشان نقدر نستورد بشكل صحيح
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from scripts.utils.hashing import get_file_hash, load_state, save_state

NORMALIZED_DIR = os.path.join(BASE_DIR, "corpus", "normalized")
RELATIONS_DIR = os.path.join(BASE_DIR, "corpus", "relations", "by_document")

def run_script(script_name, module_mode=False):
    """بيشغل السكريبتات بتاعتنا بالترتيب"""
    print(f"⏳ جاري تشغيل {script_name} ...")
    
    if module_mode:
        module_name = script_name.replace(".py", "")
        cmd = [sys.executable, "-m", f"scripts.graph.{module_name}"]
    else:
        cmd = [sys.executable, os.path.join(BASE_DIR, "scripts", script_name)]
    
    # إعداد البيئة عشان ندعم الإيموجي والرموز العربية في الويندوز
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', env=env)
    
    if result.returncode != 0:
        print(f"❌ خطأ أثناء تشغيل {script_name}:")
        print(result.stderr)
        return False
    else:
        print(f"✅ تم تشغيل {script_name} بنجاح.")
        if result.stdout:
            print(result.stdout.strip())
        return True

def main():
    print("🔍 جاري فحص الملفات للبحث عن تحديثات...")
    state = load_state()
    new_or_modified_files = []
    
    # 1. فحص ملفات الـ Normalized (المستندات والمواد)
    for root, dirs, files in os.walk(NORMALIZED_DIR):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                file_hash = get_file_hash(filepath)
                
                # لو الملف جديد أو الـ hash بتاعه اتغير
                if file_hash and (filepath not in state or state[filepath] != file_hash):
                    new_or_modified_files.append(filepath)
                    state[filepath] = file_hash

    # 2. فحص ملفات الـ Relations (العلاقات)
    for root, dirs, files in os.walk(RELATIONS_DIR):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                file_hash = get_file_hash(filepath)
                
                if file_hash and (filepath not in state or state[filepath] != file_hash):
                    new_or_modified_files.append(filepath)
                    state[filepath] = file_hash

    # لو مفيش تغييرات، نطلع
    if not new_or_modified_files:
        print("✨ مفيش ملفات جديدة أو متغيرة. الجراف محدث.")
        return

    print(f"🔄 تم اكتشاف {len(new_or_modified_files)} ملف جديد أو متغير. جاري تحديث الجراف...")
    
    # هنشغل السكريبتات بالترتيب عشان نضمن إن كل حاجة متزامنة
    # 1. نحدث المستندات
    doc_success = run_script("import_documents.py", module_mode=True)
    
    # 2. نحدث العلاقات
    rel_success = run_script("import_relations.py", module_mode=True)

    # لو حصل إيرور في أي سكريبت، منحفظش الحالة عشان نقدر نعيد المحاولة
    if not doc_success or not rel_success:
        print("⚠️ لم يتم حفظ الحالة بسبب وجود أخطاء. يرجى إصلاحها وإعادة المحاولة.")
        return

    # نحفظ الحالة الجديدة عشان المرة الجاية نعرف إحنا عالجنا إيه
    save_state(state)
    print("🎉 تم تحديث الجراف بنجاح!")

if __name__ == "__main__":
    main()
