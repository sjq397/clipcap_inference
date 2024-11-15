import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import sqlite3

def init_db():
    conn = sqlite3.connect('comments.db')  # 创建数据库文件
    c = conn.cursor()
    # 创建一个表格用于存储评论，增加 user_id 列来区分不同用户的评论
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            mkey TEXT,
            user_id TEXT,
            label TEXT,
            comment TEXT,
            PRIMARY KEY (mkey, user_id)  -- 主键由 mkey 和 user_id 组成，确保每个用户对每个 mkey 的评论唯一
        )
    ''')
    conn.commit()
    conn.close()


# 存储评论到数据库
def save_comment(mkey, user_id, label, comment):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    # 检查是否已存在此评论，若存在则更新，否则插入新评论
    c.execute('''
        INSERT OR REPLACE INTO comments (mkey, user_id, label, comment)
        VALUES (?, ?, ?, ?)
    ''', (mkey, user_id, label, comment))
    conn.commit()
    conn.close()

# 从数据库读取所有评论
def get_comments(mkey):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('SELECT user_id, comment FROM comments WHERE mkey = ?', (mkey,))
    results = c.fetchall()
    conn.close()
    return results  # 返回一个包含用户ID和评论内容的列表


def load_data(file):
    return pd.read_csv(file, sep='\t')

def load_image(url):
    try:
        if url not in st.session_state:
            response = requests.get(url)
          
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                st.session_state[url] = img  
                return img
            else:
                st.warning(f"Unable to download picture, HTTP status code: {response.status_code} ({url})")
                return None
        return st.session_state[url]
    except Exception as e:
        st.warning(f" {e} ({url})")
        return None



# Streamlit 显示图像和评论的函数
def display_images_with_comments(df, label, start_idx, end_idx):
    images_to_display = df[(df['Label'] == label)].iloc[start_idx:end_idx]
    
    num_images = len(images_to_display)
    cols = st.columns(5)  # 每行显示 5 张图片
    
    for i in range(0, num_images, 5):  
        for j in range(5):
            if i + j < num_images:
                row = images_to_display.iloc[i + j]
                col = cols[j]
                with col:
                    # 加载并显示图片
                    image = load_image(row['MUrl'])
                    if image:
                        st.image(image, caption=row['MUrl'], use_container_width=True)
                    else:
                        st.write(f"Unable to load image: {row['MUrl']} , skip this image.")
                    
                    key = row['Mkey']
                    comment_key = f"comment_{key}"
                    # 从数据库读取所有评论
                    current_comments = get_comments(key)
                    
                    # 在 session_state 中保存评论状态
                    if comment_key not in st.session_state:
                        st.session_state[comment_key] = ""
                    
                    # 显示所有评论
                    for user_id, comment in current_comments:
                        st.write(f"{user_id}: {comment}")
                    
                    # 获取当前用户输入的评论
                    user_id = st.session_state.get('user_id', 'guest')  # 获取用户ID，默认是 'guest'
                    comment = st.text_input(f"Add a comment (Mkey: {row['Mkey']}):", 
                                            value=st.session_state[comment_key], 
                                            key=f"input_{row['Mkey']}")

                    # 如果评论有变化，更新 session_state 和数据库
                    if comment != st.session_state[comment_key]:
                        st.session_state[comment_key] = comment
                        save_comment(key, user_id, label, comment)  # 将评论保存到数据库

                    if comment:
                        st.write(f"Your comment: {comment}")



def main():
    st.title('Puzzle—Image')

    # Assign a user_id, either from session or ask the user to input one
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = st.text_input("Enter your username:", "guest")
    
    uploaded_file = "golden_set_filter.tsv"
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # 初始化 SQLite 数据库
        init_db()

        if 'page_num' not in st.session_state:
            st.session_state['page_num'] = 1
        
        label = st.selectbox('Label', ['1', '0', 'uncertain'])

        page_size = 20
        page_num = st.session_state['page_num'] 
        filtered_df = df[df['Label'] == label] 
        total_pages = (len(filtered_df) // page_size) + (1 if len(filtered_df) % page_size > 0 else 0) 
        start_idx = (page_num - 1) * page_size
        end_idx = start_idx + page_size

        st.write(f"Page {page_num} of {total_pages}")

        display_images_with_comments(df, label, start_idx, end_idx)

        if 0 < page_num < total_pages:
            if st.button('Next Page'):
                st.session_state['page_num'] += 1 
                st.rerun()
        if 1 < page_num <= total_pages:
            if st.button('Last Page'):
                st.session_state['page_num'] -= 1 
                st.rerun()

if __name__ == '__main__':
    main()




if __name__ == '__main__':
    main()
