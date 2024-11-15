import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
import sqlite3
import time  # 用于生成时间戳

def init_db():
    conn = sqlite3.connect('comments.db')  # 创建数据库文件
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS comments (
            comment_id TEXT PRIMARY KEY,  -- 新增一个唯一的 comment_id
            mkey TEXT,
            user_id TEXT,
            label TEXT,
            comment TEXT
        )
    ''')
    conn.commit()
    conn.close()



def generate_comment_id(user_id, mkey):
    # 使用时间戳或一个简单的序列号生成唯一的 comment_id
    timestamp = int(time.time() * 1000)  # 获取当前时间戳（毫秒级）
    return f"{user_id}_{mkey}_{timestamp}"



def save_comment(mkey, user_id, label, comment):
    try:
        # 生成一个唯一的 comment_id
        comment_id = generate_comment_id(user_id, mkey)
        
        conn = sqlite3.connect('comments.db')
        c = conn.cursor()
        # 保存评论时使用 comment_id 作为唯一标识符
        c.execute('''
            INSERT INTO comments (comment_id, mkey, user_id, label, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (comment_id, mkey, user_id, label, comment))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"保存评论时出现错误: {e}")
        print(f"Error in save_comment: {e}")





def get_comments(mkey):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('SELECT user_id, comment FROM comments WHERE mkey = ?', (mkey,))
    results = c.fetchall()  # 获取所有评论
    conn.close()
    return results  # 返回用户ID和评论内容的列表



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
                        st.write(f"无法加载图片: {row['MUrl']} , 跳过此图片。")
                    
                    key = row['Mkey']
                    comment_key = f"comment_{key}"
                    # 从数据库读取所有评论
                    current_comments = get_comments(key)
                    
                    # 显示所有评论
                    for user_id, comment in current_comments:
                        st.write(f"{user_id}: {comment}")
                    
                    # 获取当前用户输入的评论
                    user_id = st.session_state.get('user_id', 'guest')  # 获取用户ID，默认是 'guest'
                    comment = st.text_input(f"添加评论 (Mkey: {row['Mkey']}):", 
                                            value=st.session_state.get(comment_key, ""), 
                                            key=f"input_{row['Mkey']}")  # 使用唯一的key
                    
                    # 如果评论有变化，更新 session_state 和数据库
                    if comment != st.session_state.get(comment_key, ""):
                        st.session_state[comment_key] = comment
                        save_comment(key, user_id, label, comment)  # 将评论保存到数据库

                    if comment:
                        st.write(f"您的评论: {comment}")



def main():
    st.title('Puzzle—Image')

    # 确保在会话状态中检查并设置用户 ID
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = 'guest'  # 默认用户 ID 为 'guest'

    # 提供一个输入框让用户设置自己的 ID，使用会话状态中的 user_id 来存储
    user_input = st.text_input(
        "请输入您的用户 ID", 
        value=st.session_state['user_id'],  # 通过 session_state 保持输入值
        key="user_id_input"  # 固定 key
    )
    
    # 更新会话状态中的用户 ID
    if user_input:
        st.session_state['user_id'] = user_input  # 更新用户 ID

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
