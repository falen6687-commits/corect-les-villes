import streamlit as st
import google.generativeai as genai
import os

# --- 1. إعداد الصفحة والتصميم ---
st.set_page_config(page_title="SANDIZ AI v11", layout="wide")

# تطبيق التصميم الأزرق الملكي عبر CSS
st.markdown("""
    <style>
    .main {
        background: radial-gradient(circle, #1e3a8a, #0f172a);
        color: #f1f5f9;
    }
    .stTextArea textarea {
        background-color: rgba(0,0,0,0.3) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 15px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-weight: bold !important;
        border: none !important;
    }
    h1 { text-align: center; color: #60a5fa !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. إعداد Gemini API ---
# ملاحظة: في Streamlit Cloud، نضع المفتاح في الـ Secrets
API_KEY = st.secrets.get("GEMINI_API_KEY", "AIzaSyCUYmoQKNlvCGytfv2qHO2llCAv_QloEWc")
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash') # تم التحديث لأحدث إصدار مستقر

# --- 3. إدارة المدن ---
def load_cities():
    filename = 'cities.txt'
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("casablanca\nrabat\nsale\nmeknes\nmarrakech")
    
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f.readlines() if line.strip()]

# --- 4. واجهة المستخدم ---
st.markdown("<h1>🚀 SANDIZ AI v11</h1>", unsafe_allow_html=True)

cities_db = load_cities()
ref_data = ", ".join(cities_db)

col1, col2 = st.columns(2)

with col1:
    user_input = st.text_area("📥 المدخلات:", height=400)

with col2:
    output_area = st.empty()
    result_text = output_area.text_area("✨ النتائج:", height=400, key="output", readonly=True)

if st.button("تصحيح ومطابقة ⚡"):
    if user_input.strip():
        with st.spinner("🧠 جاري البحث الذكي..."):
            prompt = f"""
            مهمتك: ربط المدخلات بالأسماء الموجودة في هذه القائمة حصراً: [{ref_data}]
            
            التعليمات:
            1. إذا أدخل المستخدم اختصاراً (مثل: كازا) ابحث عن المدينة المقابلة (casablanca).
            2. ممنوع استخدام حروف مشكلة (é, à). التزم بالحروف البسيطة.
            3. إذا لم تجد صلة، اكتب "غير موجود".
            4. أخرج النتائج سطر بسطر فقط.

            المدخلات:
            {user_input}
            """
            try:
                response = model.generate_content(prompt)
                output_area.text_area("✨ النتائج:", value=response.text.strip(), height=400)
            except Exception as e:
                st.error(f"خطأ: {str(e)}")
    else:
        st.warning("يرجى إدخال نص أولاً.")
