import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="FBL Master Cleaner", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">✈️ FBL 電報全能精簡工具</p>', unsafe_allow_html=True)
st.caption("模式：保留航班資訊、提單主行與屬性代碼，徹底剔除代理商與材積雜訊。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    
    # 定義「一定要保留」的專業屬性關鍵字 (白名單)
    attribute_white_list = ['ECC', 'EAW', 'SPX', 'HEA', 'MDK', 'CRT', 'ICE', 'PER', 'DIP']
    # 定義結構性保留標籤 (包含您要求的 3/ 航班行)
    structure_tags = ('FBL/', '3/', '5/', 'CONT', 'LAST', 'FFM')
    
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        line_upper = line.upper()
        
        # 1. 處理提單主行 (020-) 並嘗試合併屬性
        if line.startswith('020-'):
            current_awb = line
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                next_upper = next_line.upper()
                
                # 判斷下一行是否為「專業屬性代碼」且不含代理商雜訊
                if any(attr in next_upper for attr in attribute_white_list) and \
                   'WORLD-TOP' not in next_upper and 'EXPRESS' not in next_upper:
                    current_awb = f"{line} {next_line}"
                    i += 1 # 消耗掉下一行
            cleaned_lines.append(current_awb)
            
        # 2. 處理航班資訊與結構標記 (如 3/LH8013...)
        elif any(line.startswith(tag) for tag in structure_tags):
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
        label="📥 下載全能精簡版 TXT",
        data=result_text,
        file_name=f"FBL_Master_Clean.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽結果", "🔍 原始數據"])
    with tab1:
        st.text_area("預覽：已保留航班資訊與合併屬性", value=result_text, height=450)
    with tab2:
        st.text_area("原始 Word 內容", value="\n".join(raw_lines), height=450)
