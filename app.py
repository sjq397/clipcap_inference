import pandas as pd
import streamlit as st

# 读取 TSV 文件
file_path = r"C:\Users\v-jiqingsang\Desktop\Prompt_Topic\202502191745373292.tsv"
df = pd.read_csv(file_path, sep='\t')

# 显示筛选选项
st.sidebar.header("筛选选项")
# image_score = st.sidebar.slider('Overall Image Score', min_value=int(df['Result.OverallImageScore'].min()), max_value=int(df['Result.OverallImageScore'].max()), value=(int(df['Result.OverallImageScore'].min()), int(df['Result.OverallImageScore'].max())))
relevance_score = st.sidebar.slider('Overall Relevance Score', min_value=int(df['Result.OverallRelevanceScore'].min()), max_value=int(df['Result.OverallRelevanceScore'].max()), value=(int(df['Result.OverallRelevanceScore'].min()), int(df['Result.OverallRelevanceScore'].max())))
# language_score = st.sidebar.slider('Overall Language Score', min_value=int(df['Result.OverallLanguageScore'].min()), max_value=int(df['Result.OverallLanguageScore'].max()), value=(int(df['Result.OverallLanguageScore'].min()), int(df['Result.OverallLanguageScore'].max())))
consistency_score = st.sidebar.slider('Overall Consistency Score', min_value=int(df['Result.OverallReadabilityScore'].min()), max_value=int(df['Result.OverallReadabilityScore'].max()), value=(int(df['Result.OverallReadabilityScore'].min()), int(df['Result.OverallReadabilityScore'].max())))

# # 根据筛选条件过滤数据
# filtered_df = df[
#     (df['Result.OverallImageScore'] >= image_score[0]) & (df['Result.OverallImageScore'] <= image_score[1]) &
#     (df['Result.OverallRelevanceScore'] >= relevance_score[0]) & (df['Result.OverallRelevanceScore'] <= relevance_score[1]) &
#     (df['Result.OverallLanguageScore'] >= language_score[0]) & (df['Result.OverallLanguageScore'] <= language_score[1]) &
#     (df['Result.OverallReadabilityScore'] >= consistency_score[0]) & (df['Result.OverallReadabilityScore'] <= consistency_score[1])
# ]

# 根据筛选条件过滤数据
filtered_df = df[
    (df['Result.OverallRelevanceScore'] >= relevance_score[0]) & (df['Result.OverallRelevanceScore'] <= relevance_score[1]) &
    (df['Result.OverallReadabilityScore'] >= consistency_score[0]) & (df['Result.OverallReadabilityScore'] <= consistency_score[1])
]

# 分页显示图片和信息
page_size = 10
page_number = st.sidebar.number_input('Page Number', min_value=1, max_value=(len(filtered_df) // page_size) + 1, value=1)
start_idx = (page_number - 1) * page_size
end_idx = start_idx + page_size

# 显示图片和对应信息
for idx, row in filtered_df.iloc[start_idx:end_idx].iterrows():
    st.image(row['MUrl'], caption=row['Topic'])
    st.write(f"**Topic:** {row['Topic']}")
    st.write(f"**MUrl:** {row['MUrl']}")
    # st.write(f"**Description:** {row['Description']}")
    st.write(f"**PageTitle:** {row['PageTitle']}")
    # st.write(f"**Overall Image Score:** {row['Result.OverallImageScore']}")
    st.write(f"**Overall Relevance Score:** {row['Result.OverallRelevanceScore']}")
    # st.write(f"**Overall Language Score:** {row['Result.OverallLanguageScore']}")
    st.write(f"**Overall Readability Score:** {row['Result.OverallReadabilityScore']}")
    st.write("---")

# 运行 Streamlit 应用
if __name__ == "__main__":
    st.title("Result Entity Visualization")
    st.write("根据筛选条件显示图片和对应信息")