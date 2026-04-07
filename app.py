import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="AWB Smart Merger", page_icon="🔗", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">🔗 FBL 提單智能合併工具 (V7)</p>', unsafe_allow_html=True)
st.caption("模式：僅合併 020- 與「專業屬性代碼」(如 SH/EAWECC)，自動剔除代理商名稱。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    
    # 定義「一定要保留」的專業屬性關鍵字 (白名單)
    attribute_white_list = ['ECC', 'EAW', 'SPX', 'HEA', 'MDK', 'CRT', 'ICE', 'PER', 'DIP']
    
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        line_upper = line.upper()
        
        # 1. 處理提單主行 (020-)
        if line.startswith('020-'):
            current_awb = line
            # 檢查下一行是否包含白名單中的專業代碼
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                next_upper = next_line.upper()
                
                # 只有當下一行包含白名單代碼，且不包含黑名單字眼時才合併
                if any(attr in next_upper for attr in attribute_white_list) and \
                   'WORLD-TOP' not in next_upper and 'QUALITY' not in next_upper:
                    current_awb = f"{line} {next_line}"
                    i += 1 # 消耗下一行
            
            cleaned_lines.append(current_awb)
            
        # 2. 保留：結構標記與航點
        elif any(line.startswith(tag) for tag in ('FBL/', '5/', 'CONT', 'LAST', 'FFM')) or \
             (len(line) == 3 and line.isupper() and line.isalpha()):
            cleaned_lines.append(line)
            
        i += 1

    result_text = "\n".join(cleaned_lines)
    awb_count = len([l for l in cleaned_lines if l.startswith('020-')])

    # 3. 顯示與下載
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 合併後提單數", f"{awb_count} 筆")
    col2.metric("📝 總輸出行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載 V7 智能合併版 TXT",
        data=result_text,
        file_name=f"FBL_Smart_Clean.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("預覽：SH/EAWECC 已保留，WORLD-TOP 已剔除", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
