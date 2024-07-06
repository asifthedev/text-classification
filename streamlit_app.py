from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import json


# Set API key
API_KEY = 'AIzaSyBmDMAMg8Ct-mnbyZdnvHwkPNmPtNbKGcE'

# Function to extract video ID from YouTube URL
def extract_video_id(url):
    regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([^"&?\/\n\s]{11})'
    match = re.search(regex, url)
    if match:
        return match.group(1)
    else:
        return None

# Function to get video comments
def get_video_comments(video_id):
    try:
        youtube = build('youtube', 'v3', developerKey=API_KEY)
        comments = []
        next_page_token = None
        
        # Retrieve comments using the YouTube API
        while True:
            response = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            ).execute()
            
            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment)
            
            next_page_token = response.get('nextPageToken')
            
            if not next_page_token:
                break
        
        return comments
    
    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return []

def get_comments(url):
    # Example YouTube video URL
    youtube_url = url
    
    # Extract video ID from URL
    video_id = extract_video_id(youtube_url)
    
    if video_id:
        video_comments = get_video_comments(video_id)
        video_data = {
            'comments': {
                'length': len(video_comments),
                'text': video_comments
            }
        }
        
        with open('video.json', 'w', encoding='utf-8') as f:
            json.dump(video_data, f, ensure_ascii=False, indent=4)
        
        print(f'Successfully saved {len(video_comments)} comments to video.json.')
        
    else:
        print('Invalid YouTube URL or unable to extract video ID.')



import streamlit as st
import transformers
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
