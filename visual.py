import streamlit as st
import pandas as pd

# Load the TSV file
@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path, sep='\t', header=0)
    data['Position'] = range(1, len(data) + 1)
    
    return data

# Function to get images for selected titles
def get_images_for_titles(data, selected_titles):
    return data[data['MMAltTextWords'].isin(selected_titles)].sort_values(by='Position')

# Function to truncate text
def truncate_text(text, max_length=30):
    if len(text) > max_length:
        return text[:max_length] + '...'
    return text

# Streamlit app
def main():
    st.title("Title-Based Image Picker")

    # Load data
    file_path = "Bmq_infer_test.tsv"
    data = load_data(file_path)

    # Get unique titles
    titles = data['MMAltTextWords'].unique()

    # Multiselect titles
    selected_titles = st.multiselect("Choose Titles", titles)

    if selected_titles:
        # Display selected titles
        st.write(f"### Selected Titles")

        # Get images for the selected titles
        images = get_images_for_titles(data, selected_titles)

        # Display images with truncated titles, 'Bmq', and 'Bmq_Infer'
        cols = st.columns(5)
        for i, row in images.iterrows():
            with cols[(row['Position'] - 1) % 5]:
                st.image(row['MUrl'], width=150, caption=truncate_text(row['MMAltTextWords']), use_column_width=True)
                st.write(f"Title: {row['MMAltTextWords']}")
                st.write(f"Bmq: {row['Bmq']}")
                st.write(f"Bmq_Infer: {row['Bmq_Predict']}")
                st.write(" ")
                st.write(" ")

if __name__ == "__main__":
    main()
