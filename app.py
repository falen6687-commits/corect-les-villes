import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
import os
import json

# --- 1. إعداد Gemini API ---
# حاول جلب المفتاح من Secrets أو استخدم المباشر (الأفضل وضعه في Secrets)
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyCUYmoQKNlvCGytfv2qHO2llCAv_QloEWc")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. إدارة ملف المدن ---
def load_cities_from_file():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech")
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 3. الواجهة (بنفس كود HTML/CSS الخاص بك) ---
HTML_UI = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <style>
        body { background: radial-gradient(circle, #1e3a8a, #0f172a); color: #f1f5f9; font-family: 'Segoe UI', sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; overflow: hidden; }
        .container { width: 95%; max-width: 1000px; background: rgba(255, 255, 255, 0.05); padding: 30px; border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); }
        h1 { text-align: center; color: #60a5fa; margin-bottom: 20px; font-size: 24px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; }
        textarea { width: 100%; height: 350px; background: rgba(0,0,0,0.3); color: #fff; border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 15px; font-size: 15px; resize: none; box-sizing: border-box; outline: none; }
        .btn-main { width: 100%; padding: 15px; background: #2563eb; color: white; border: none; border-radius: 12px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .btn-main:hover { background: #1d4ed8; }
        #status { display: none; text-align: center; color: #60a5fa; margin-top: 10px; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 SANDIZ AI v11</h1>
        <div class="grid">
            <div><label>📥 المدخلات:</label><textarea id="in"></textarea></div>
            <div><label>✨ النتائج:</label><textarea id="out" readonly></textarea></div>
        </div>
        <div id="status">🧠 جاري البحث الذكي...</div>
        <button class="btn-main" onclick="run()">تصحيح ومطابقة ⚡</button>
    </div>

    <script>
        function run() {
            const input = document.getElementById('in').value;
            if(!input.trim()) return;
            
            document.getElementById('status').style.display = 'block';
            
            // إرسال البيانات إلى Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: input
            }, '*');
        }

        // استقبال النتائج من Streamlit
        window.addEventListener('message', function(event) {
            if (event.data.type === 'set_result') {
                document.getElementById('out').value = event.data.result;
                document.getElementById('status').style.display = 'none';
            }
        });
    </script>
</body>
</html>
"""

# إعداد عرض الصفحة
st.set_page_config(page_title="SANDIZ AI", layout="wide")

# عرض واجهة HTML داخل Streamlit
# نستخدم حيلة لاستقبال البيانات من JavaScript
value = components.html(HTML_UI, height=700)

# منطق المعالجة (الذي كان في /ai_call)
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

# البحث عن أي رسائل قادمة من الـ JavaScript (عبر الحاوية)
# ملاحظة: Streamlit لا يدعم الرجوع المباشر للقيم بسهولة من HTML مخصص، 
# لذا سنستخدم مدخل مخفي بسيط لتسهيل الربط
user_input = st.text_input("إدخال تقني (يمكنك تجاهله)", key="hidden_in", label_visibility="collapsed")

if user_input and user_input != st.session_state.last_input:
    st.session_state.last_input = user_input
    cities_db = load_cities_from_file()
    ref_data = ", ".join(cities_db)
    
    prompt = f"""
    مهمتك: ربط المدخلات بالأسماء الموجودة في هذه القائمة حصراً: [{ref_data}]
    1. الاختصارات (كازا) تحول للاسم الكامل (casablanca).
    2. لا حروف مشكلة.
    3. إذا لم تجد، اكتب "غير موجود".
    4. النتائج سطر بسطر.
    المدخلات:
    {user_input}
    """
    
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        # إرسال النتيجة مرة أخرى إلى HTML (سيحتاج المستخدم لإعادة الضغط أو نستخدم Spinner)
        st.write(f"✅ تمت المعالجة. انسخ النتائج من المربع الأزرق.")
        st.code(result) # عرض احتياطي للنتائج لضمان عملها في السحابة
    except Exception as e:
        st.error(f"خطأ: {e}")
