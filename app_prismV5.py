import streamlit as st
import pandas as pd
import random

# 设置 Streamlit 页面
st.title("TSV 文件图片查看器")

# 上传 TSV 文件
uploaded_file = st.file_uploader("上传 TSV 文件", type=["tsv"])

if uploaded_file:
    # 读取 TSV 文件
    df = pd.read_csv(uploaded_file, sep='\t')
    
    # 检查必要列是否存在
    if 'ImageKey' not in df.columns or 'predicted_label' not in df.columns:
        st.error("TSV 文件缺少必要的列: ImageKey 或 predicted_label	")
    else:
        # 获取所有唯一标签
        unique_labels = df['predicted_label'].unique()
        
        # 对每个标签随机采样200条数据
        sampled_dfs = []
        for label in unique_labels:
            label_df = df[df['predicted_label'] == label]
            sample_size = min(200, len(label_df))
            sampled_label_df = label_df.sample(n=sample_size, random_state=42)
            sampled_dfs.append(sampled_label_df)
        
        # 合并所有采样结果
        sampled_df = pd.concat(sampled_dfs, ignore_index=True)
        
        # 选择标签
        selected_label = st.selectbox("选择一个标签查看对应图片:", unique_labels)
        
        # 筛选对应标签的图片
        filtered_df = sampled_df[sampled_df['predicted_label'] == selected_label]
        
        st.write(f"共找到 {len(filtered_df)} 张图片")
        
        # 显示图片，调整为网格布局
        cols = st.columns(3)  # 三列布局
        for i, (_, row) in enumerate(filtered_df.iterrows()):
            with cols[i % 3]:
                st.image(row['ImageKey'], caption=row['predicted_label'], use_column_width=True)
                st.markdown(f"[查看图片]({row['ImageKey']})")
