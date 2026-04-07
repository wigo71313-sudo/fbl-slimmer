import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="FBL AWB Slimmer V2", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">📦 FBL 提單雙行精簡工具</p>', unsafe_allow_html=True)
st.caption("修正版：嚴格執行『僅保留 020- 及其直接下方行』，徹底過濾 DIM 下方雜訊。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 請上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    # 核心邏輯控制：只有這兩個標籤開頭的行，才允許「抓取下一行」
    allow_next_line = False
    
    # 定義結構性保留標籤
    structure_tags = ('FBL/', '5/', 'CONT', 'LAST', 'FFM')
    # 定義絕對刪除標籤 (黑名單)
    black_list = ('DIM/', 'SSR/', 'OSI/', 'COR/', 'OCI/', 'AGENT', 'HAWB')
    
    for line in raw_lines:
        # A. 如果是提單主行 (020-)：保留，並開啟下一行抓取權限
        if line.startswith('020-'):
            cleaned_lines.append(line)
            allow_next_line = True
            continue
            
        # B. 如果擁有抓取權限，且這一行不是黑名單，也不是另一行提單：保留它並關閉權限
        if allow_next_line:
            allow_next_line = False # 權限立刻用完
            # 檢查這一行是否不小心撞到黑名單（預防萬一）
            if not any(line.startswith(b) for b in black_list):
                cleaned_lines.append(line)
            continue
            
        # C. 處理 ULD (不開啟下一行權限)
        if line.startswith('ULD/'):
            parts = line.split('/')
            if len(parts) >= 2:
                uld_id = parts[1].split()[0]
                line = f"ULD/{uld_id}"
            cleaned_lines.append(line)
            allow_next_line = False
            continue
            
        # D. 處理結構標記與航點 (不開啟下一行權限)
        if any(line.startswith(tag) for tag in structure_tags) or (len(line) == 3 and line.isupper() and line.isalpha()):
            cleaned_lines.append(line)
            allow_next_line = False
            continue

        # E. 其他所有情況 (包括 DIM/ 及其下方的 /K56...) 全部跳過
        continue

    # 數據結果
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    result_text = "\n".join(cleaned_lines)

    # 3. 顯示結果
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 提單總數", f"{len(awb_set)} 筆")
    col2.metric("📝 清理後總行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載修正版 TXT",
        data=result_text,
        file_name=f"FBL_Fixed_{uploaded_file.name.replace('.docx', '')}.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("清理後的內容", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
