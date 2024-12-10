import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

# 数据文件路径
data_file = "visual_Index_infer_sample_1210.tsv"

# 读取数据
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, sep='\t')
    return data

# 加载远程图片
def load_image_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except requests.RequestException as e:
        st.warning(f"Failed to load image: {url}")
        return None

# 主函数
def main():
    st.title("Puzzle Output Visualizer")
    st.sidebar.header("Options")
    
    # 加载数据
    data = load_data(data_file)
    
    # 检查是否包含必要的列
    if 'Puzzle_output' not in data.columns or 'MUrl' not in data.columns:
        st.error("The dataset must contain 'Puzzle_output' and 'MUrl' columns.")
        return

    # 输入桶范围
    min_val = st.sidebar.slider("Min Puzzle_output", 0.0, 1.0, 0.0, step=0.1)
    max_val = st.sidebar.slider("Max Puzzle_output", 0.0, 1.0, 1.0, step=0.1)
    
    # 过滤数据
    filtered_data = data[(data['Puzzle_output'] >= min_val) & (data['Puzzle_output'] <= max_val)]
    
    if filtered_data.empty:
        st.warning("No data found for the selected range.")
        return
    
    # 分页功能
    page_size = 10
    total_pages = (len(filtered_data) + page_size - 1) // page_size
    page = st.sidebar.number_input("Page Number", min_value=1, max_value=total_pages, value=1)
    
    # 当前页数据
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_data = filtered_data.iloc[start_idx:end_idx]
    
    st.write(f"Showing images for Puzzle_output in range [{min_val}, {max_val}] - Page {page}/{total_pages}")
    
    # 显示图片
    for idx, row in page_data.iterrows():
        image_url = row['MUrl']
        puzzle_value = row['Puzzle_output']
        
        # 加载并显示图片
        image = load_image_from_url(image_url)
        if image:
            st.image(image, caption=f"Puzzle_output: {puzzle_value}", use_container_width=True)

if __name__ == "__main__":
    main()
