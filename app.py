import streamlit as st
import google.generativeai as genai
import os

# --- 1. إعدادات الصفحة (لإخفاء عناصر Streamlit الافتراضية) ---
st.set_page_config(page_title="SANDIZ AI v11", layout="wide")

# --- 2. إعداد Gemini API ---
# يفضل وضع المفتاح في Streamlit Secrets، أو استخدامه مباشرة هنا
# هذا السطر يقرأ المفتاح من صفحة Secrets التي فتحتها الآن
API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- 3. وظيفة جلب المدن ---
def load_cities_from_file():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech")
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 4. التصميم (CSS) للحفاظ على المظهر الملكي ---
st.markdown("""
    <style>
    /* الخلفية والتنسيق العام */
    .stApp {
        background: radial-gradient(circle, #1e3a8a, #0f172a);
        color: #f1f5f9;
    }
    /* تنسيق مربعات النص */
    .stTextArea textarea {
        background-color: rgba(0,0,0,0.3) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
        font-size: 16px !important;
    }
    /* تنسيق الزر */
    .stButton>button {
        width: 100%;
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    h1 { text-align: center; color: #60a5fa !important; font-family: 'Segoe UI', sans-serif; }
    label { color: #60a5fa !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. واجهة المستخدم ---
st.markdown("<h1>🚀 SANDIZ AI v11</h1>", unsafe_allow_html=True)

cities_db = load_cities_from_file()
ref_data = ", ".join(cities_db)

# إنشاء الأعمدة كما في تصميمك الأصلي
col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area("📥 المدخلات:", height=400, placeholder="أدخل المدن هنا (كازا، الرباط...)")

# مكان مخصص للنتائج
if "ai_result" not in st.session_state:
    st.session_state.ai_result = ""

with col2:
    st.text_area("✨ النتائج:", value=st.session_state.ai_result, height=400, disabled=True)

# زر التشغيل
if st.button("تصحيح ومطابقة ⚡"):
    if user_input.strip():
        with st.spinner("🧠 جاري البحث الذكي..."):
            prompt = f"""
            مهمتك: ربط المدخلات بالأسماء الموجودة في هذه القائمة حصراً: [{ref_data}]
            1. الاختصارات (كازا) تحول للاسم الكامل (casablanca).
            2. لا حروف مشكلة (é, à).
            3. إذا لم تجد، اكتب "غير موجود".
            4. النتائج سطر بسطر.
            المدخلات:
            {user_input}
            """
            try:
                response = model.generate_content(prompt)
                st.session_state.ai_result = response.text.strip()
                st.rerun() # إعادة التشغيل لتحديث مربع النص
            except Exception as e:
                st.error(f"حدث خطأ: {e}")
    else:
        st.warning("الرجاء إدخال بيانات أولاً.")
