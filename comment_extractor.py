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

# Example usage:
if __name__ == '__main__':
    get_comments('https://www.youtube.com/watch?v=M8ea_6JbBCY')
