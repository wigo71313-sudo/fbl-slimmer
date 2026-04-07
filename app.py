import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="FBL Strict Twin-Line", page_icon="✂️", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">✂️ FBL 絕對雙行提取工具</p>', unsafe_allow_html=True)
st.caption("模式：每一筆提單僅保留「主行」與「其下一行」，徹底切斷所有後續雜訊。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        
        # 核心規則：只認 020- 開頭的行
        if line.startswith('020-'):
            # 1. 抓取提單主行
            cleaned_lines.append(line)
            
            # 2. 嘗試抓取「絕對下一行」
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                # 只要下一行不是另一筆提單，就抓進來
                if not next_line.startswith('020-'):
                    cleaned_lines.append(next_line)
                    i += 1 # 消耗掉這行，防止重複處理
            
            # 抓完這兩行後，後續的 DIM/, SSR/, QUALITY EXPRESS 等等
            # 會因為不符合 startswith('020-') 而被 while 迴圈直接跳過
            
        # 額外保留：電報結構標記 (可選，若不需要可刪除此段)
        elif any(line.startswith(tag) for tag in ('FBL/', '5/', 'CONT', 'LAST', 'FFM')):
            cleaned_lines.append(line)
        
        # 額外保留：目的地航點 (如 FRA, TPE)
        elif len(line) == 3 and line.isupper() and line.isalpha():
            cleaned_lines.append(line)

        i += 1

    # 數據結果
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    result_text = "\n".join(cleaned_lines)

    # 3. 統計與下載
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 提單總數", f"{len(awb_set)} 筆")
    col2.metric("📝 總輸出行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載絕對雙行版 TXT",
        data=result_text,
        file_name=f"FBL_Strict_Twin.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("清理後的內容 (僅保留提單及首行描述)", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
