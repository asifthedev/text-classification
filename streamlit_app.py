import streamlit as st
import transformers
from comment_extractor import get_comments
import json

# Caching model using streamlit
@st.cache_resource
def cache_model():
    return transformers.pipeline("text-classification")

# Check if 'saved_model' is in the current directory
with st.spinner('Downloading model ...'):
    classify = cache_model()

# Setting page title
st.title(":red[Text] Classification")

# Input text box
url = st.text_input("Enter video URL")

# Loading the saved model from the directory
comment_stat = {'total': 0, 'positive': 0, 'negative': 0}
total_comments_with_label = []

# Classification button
if st.button("Classify"):
    if url:
        with st.spinner("Loading Comments..."):
            get_comments(url)
            

        with open('video.json', 'r', encoding='utf-8') as f:
            video = json.load(f)

            # Total Comments
            comment_stat["total"] = video["comments"]["length"]

            # Grabbing List of comments
            video_comments = video["comments"]["text"]

            with st.spinner("Making prediction..."):
                for comment in video_comments:
                    result = classify(comment)
                    total_comments_with_label.append({"comment": comment, "label": result[0]['label']})
                    if result[0]['label'] == "POSITIVE":
                        comment_stat["positive"] += 1
                    else:
                        comment_stat['negative'] += 1

        # Displaying metrics in a row
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", comment_stat["total"])
        with col2:
            st.metric("Positive", comment_stat["positive"])
        with col3:
            st.metric("Negative", comment_stat["negative"])

    else:
        st.warning("Please enter a video URL to classify.")

    st.write(total_comments_with_label)
