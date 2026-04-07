import streamlit as st
from docx import Document

# 1. 頁面配置
st.set_page_config(page_title="AWB Single Line Merger", page_icon="🔗", layout="wide")

st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; color: #1E3A8A; font-weight: 800; }
    .stMetric { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-header">🔗 FBL 提單單行合併工具</p>', unsafe_allow_html=True)
st.caption("模式：將 020- 主行與其下一行屬性合併為一行，其餘雜訊全數剔除。")

# 2. 上傳區
uploaded_file = st.file_uploader("📂 上傳 FBL Word 檔案 (.docx)", type="docx")

if uploaded_file is not None:
    doc = Document(uploaded_file)
    raw_lines = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    
    cleaned_lines = []
    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        
        # 核心規則：處理提單主行 (020-)
        if line.startswith('020-'):
            current_awb = line
            # 檢查下一行是否為描述行，如果是則合併
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i+1]
                # 排除條件：確保下一行不是雜訊或另一筆提單
                exclude_keywords = ('QUALITY EXPRESS', 'DIM/', 'SSR/', 'AGENT', 'HAWB', 'CMT', 'OSI/')
                if not any(kw in next_line.upper() for kw in exclude_keywords) and not next_line.startswith('020-'):
                    # 合併主行與下一行，中間加一個空格
                    current_awb = f"{line} {next_line}"
                    i += 1 # 跳過下一行
            
            cleaned_lines.append(current_awb)
            
        # 保留：結構標記與航點 (如 FRA)
        elif any(line.startswith(tag) for tag in ('FBL/', '5/', 'CONT', 'LAST', 'FFM')) or \
             (len(line) == 3 and line.isupper() and line.isalpha()):
            cleaned_lines.append(line)
            
        i += 1

    # 數據結果
    result_text = "\n".join(cleaned_lines)
    awb_count = len([l for l in cleaned_lines if l.startswith('020-')])

    # 3. 顯示與下載
    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("📄 合併後提單數", f"{awb_count} 筆")
    col2.metric("📝 總輸出行數", f"{len(cleaned_lines)} 行")

    st.download_button(
        label="📥 下載單行合併版 TXT",
        data=result_text,
        file_name=f"AWB_Merged_Lines.txt",
        mime="text/plain",
        use_container_width=True
    )

    tab1, tab2 = st.tabs(["📋 預覽合併結果", "🔍 原始數據"])
    with tab1:
        st.text_area("清理後的內容 (主行與描述已合併)", value=result_text, height=450)
    with tab2:
        st.text_area("原始內容", value="\n".join(raw_lines), height=450)
