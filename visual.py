import streamlit as st
import pandas as pd
import requests
from PIL import Image
from io import BytesIO


def load_data(file):
    return pd.read_csv(file, sep='\t')

def display_images_with_comments(df, label, start_idx, end_idx):
    images_to_display = df[(df['Label'] == label)].iloc[start_idx:end_idx]
    
    num_images = len(images_to_display)
    

    cols = st.columns(5)  
    for i in range(0, num_images, 5):  
        for j in range(5):
            if i + j < num_images:
                row = images_to_display.iloc[i + j]
                col = cols[j]
                with col:

                    image = load_image(row['MUrl'])
                    if image:
                        st.image(image, caption=row['MUrl'], use_container_width=True)
                    else:

                        st.write(f"Unable to load image: {row['MUrl']} , skip this image.")
                    
   
                    key = row['Mkey']
                    comment_key = f"comment_{key}"
                    if comment_key not in st.session_state:
                        st.session_state[comment_key] = ""  
                    
                    comment = st.text_input(f"comment (Mkey: {row['Mkey']}):", 
                                            value=st.session_state[comment_key], 
                                            key=f"input_{row['Mkey']}")
                    
                    if comment != st.session_state[comment_key]:
                        st.session_state[comment_key] = comment

                    if comment:
                        st.write(f"comment: {comment}")


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

def main():
    st.title('Puzzle—Image')

    uploaded_file = r"C:\Users\v-jiqingsang\Desktop\Image_icon\Code\data\goldenset\golden_set_filter.tsv"
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        
        # 初始化page_num，如果没有存储在session_state中
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

        if 0< page_num < total_pages:
            if st.button('Next Page'):
                st.session_state['page_num'] += 1 
                st.rerun()  
        if 1< page_num <= total_pages:
            if st.button('Last Page'):
                st.session_state['page_num'] -= 1 
                st.rerun()  



if __name__ == '__main__':
    main()
