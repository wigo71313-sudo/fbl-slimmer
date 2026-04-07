import streamlit as st
from docx import Document

st.set_page_config(page_title="FBL AWB Slimmer V4", page_icon="📦", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">📦 FBL 提單雙行精簡工具 (終極版)</p>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    
    # 建立一個緩衝區，一次處理一組數據
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        
        # 1. 處理提單主行 (020-)
        if line.startswith('020-'):
            current_awb_block = [line]
            # 檢查下一行是否是描述行
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                # 排除條件：如果下一行包含這些關鍵字，就不抓它
                exclude_keywords = ('QUALITY EXPRESS', 'DIM/', 'SSR/', 'AGENT', 'HAWB', 'CMT', 'OSI/')
                if not any(kw in next_line.upper() for kw in exclude_keywords) and not next_line.startswith('020-'):
                    current_awb_block.append(next_line)
                    i += 1 # 跳過下一行，因為已經抓進來了
            
            cleaned_lines.extend(current_awb_block)
            
        # 2. 處理裝備主行 (ULD/)
        elif line.startswith('ULD/'):
            parts = line.split('/')
            if len(parts) >= 2:
                uld_id = parts[1].split()[0]
                cleaned_lines.append(f"ULD/{uld_id}")
                
        # 3. 處理結構標記與航點 (如 FBL, CONT, FRA)
        elif any(line.startswith(tag) for tag in ('FBL/', '5/', 'CONT', 'LAST', 'FFM')) or (len(line) == 3 and line.isupper() and line.isalpha()):
            cleaned_lines.append(line)
            
        i += 1

    # 數據結果
    awb_set = set([l[:12] for l in cleaned_lines if l.startswith('020-')])
    result_text = "\n".join(cleaned_lines)

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 提單總數", f"{len(awb_set)} 筆")
    col2.metric("📝 清理後總行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載最終淨化版 TXT",
        data=result_text,
        file_name=f"FBL_Final_Clean.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("清理後的內容", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
