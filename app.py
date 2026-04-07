import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="FBL AWB Slimmer", page_icon="📦", layout="wide")

# 2. 自定義介面美化
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">📦 FBL 提單雙行精簡工具</p>', unsafe_allow_html=True)
st.caption("功能：保留 020- 提單行及其下一行屬性描述，自動剔除 DIM/SSR/OSI 雜訊。")

# 3. 上傳區
uploaded_file = st.file_uploader("📂 請上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    just_saw_awb = False
    
    # 結構性標記
    structure_tags = ('FBL/', '5/', 'CONT', 'LAST', 'FFM')
    
    for line in raw_lines:
        # A. 提單主行 (020-)：保留並標記下一行也要抓
        if line.startswith('020-'):
            cleaned_lines.append(line)
            just_saw_awb = True
            continue
            
        # B. 抓取提單後的首行描述 (如 A/ECC...)
        if just_saw_awb:
            cleaned_lines.append(line)
            just_saw_awb = False
            continue
            
        # C. 裝備主行 (ULD/)：保留並優化
        if line.startswith('ULD/'):
            parts = line.split('/')
            if len(parts) >= 2:
                uld_id = parts[1].split()[0]
                line = f"ULD/{uld_id}"
            cleaned_lines.append(line)
            just_saw_awb = False
            continue
            
        # D. 電報結構標記與航點：保留
        if any(line.startswith(tag) for tag in structure_tags) or (len(line) == 3 and line.isupper() and line.isalpha()):
            cleaned_lines.append(line)
            just_saw_awb = False
            continue

    # 數據結果
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    result_text = "\n".join(cleaned_lines)

    # 4. 統計儀表板
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 提單總數", f"{len(awb_set)} 筆")
    col2.metric("📝 清理後行數", f"{len(cleaned_lines)} 行")

    # 5. 下載與預覽
    st.download_button(
        label="📥 下載雙行精簡版 TXT",
        data=result_text,
        file_name=f"FBL_Slim_{uploaded_file.name.replace('.docx', '')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("清理後的內容", value=result_text, height=450)
    with tab2:
        st.text_area("原始 Word 內容", value="\n".join(raw_lines), height=450)
else:
    st.info("💡 提示：上傳後將自動為您提取提單號與 ECC/SH 等屬性代碼。")
