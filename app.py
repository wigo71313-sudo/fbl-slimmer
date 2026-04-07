import streamlit as st
from docx import Document
import re

# 1. 頁面配置
st.set_page_config(page_title="FBL Master Cleaner V9", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">✈️ FBL 電報精進工具 V9</p>', unsafe_allow_html=True)
st.caption("更新：自動保留所有數字開頭的結構行 (如 3/, 5/, 8/)，並維持提單屬性合併。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    
    # 定義專業屬性關鍵字 (白名單)
    attribute_white_list = ['ECC', 'EAW', 'SPX', 'HEA', 'MDK', 'CRT', 'ICE', 'PER', 'DIP']
    
    # 定義文字型結構標籤
    text_structure_tags = ('FBL/', 'CONT', 'LAST', 'FFM')
    
    # 黑名單關鍵字 (防止誤抓代理商)
    kill_keywords = ('WORLD-TOP', 'OVERSEA', 'QUALITY', 'EXPRESS', 'DIM/', 'SSR/', 'AGENT')
    
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        line_upper = line.upper()
        
        # 1. 處理提單主行 (020-) 並合併屬性
        if line.startswith('020-'):
            current_awb = line
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                next_upper = next_line.upper()
                
                # 判斷下一行是否為專業屬性且不含黑名單
                if any(attr in next_upper for attr in attribute_white_list) and \
                   not any(kill in next_upper for kill in kill_keywords):
                    current_awb = f"{line} {next_line}"
                    i += 1 
            cleaned_lines.append(current_awb)
            
        # 2. 處理航班與結構標誌：
        #    符合「數字/」開頭 (如 3/, 5/, 8/) 或在文字結構標籤內
        elif re.match(r'^\d/', line) or any(line.startswith(tag) for tag in text_structure_tags):
            cleaned_lines.append(line)
            
        # 3. 處理目的地航點 (如 FRA)
        elif len(line) == 3 and line.isupper() and line.isalpha():
            cleaned_lines.append(line)
            
        i += 1

    result_text = "\n".join(cleaned_lines)
    awb_count = len([l for l in cleaned_lines if l.startswith('020-')])

    # 3. 顯示結果
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 提單總數", f"{awb_count} 筆")
    col2.metric("📝 剩餘總行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載 V9 最終版 TXT",
        data=result_text,
        file_name=f"FBL_V9_Final.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("預覽：已自動識別並保留 3/, 5/, 8/ 等航班資訊", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
