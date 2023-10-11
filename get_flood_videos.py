import requests
import os
import pandas as pd

# Replace 'YOUR_BEARER_TOKEN' with your actual Twitter API bearer token
BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAADoYqAEAAAAAniozMrgExuLSJ7oQaHSYVI0GLrw%3DnCF2ebXHe4gZqCxh4PXBkvIQeUGGSE6old2dyiD7MPfsoKfTOu'

hashtag = 'πλημμυρες' 

# Define the API endpoint URL
url = 'https://api.twitter.com/2/tweets/search/recent'

# Define the query parameters
params = {
    'query': f'#{hashtag} has:videos -is:retweet -is:reply',
    'tweet.fields': 'author_id,attachments,created_at',
    'expansions': 'attachments.media_keys',
    'media.fields': 'variants',
    'max_results': 10
}

# Define the headers with the Authorization token
headers = {
    'Authorization': f'Bearer {BEARER_TOKEN}'
}

# Send the GET request
response = requests.get(url, params=params, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Extract tweet data
    tweets = data.get('data', [])
    
    # Extract media data
    media = data.get('includes', {}).get('media', [])
    
    # Create DataFrames from tweet and media data
    df_tweets = pd.DataFrame(tweets)
    df_media = pd.DataFrame(media)
    
    # Drop rows with NaN values in the 'variants' column
    df_media = df_media.dropna(subset=['variants'])

    # Extract video URLs from the 'variants' column
    video_urls = []
    for variants in df_media['variants']:
        video_url = next((variant['url'] for variant in variants if variant.get('content_type') == 'video/mp4'), None)
        video_urls.append(video_url)

    # Ensure that the 'video_urls' list has the same length as 'df_tweets' by adding None for missing values
    while len(video_urls) < len(df_tweets):
        video_urls.append(None)

   # Ensure that the 'video_urls' list has the same length as 'df_tweets' by adding None for missing values
    while len(video_urls) > len(df_tweets):
        df_tweets = df_tweets.append(pd.Series(dtype='object'), ignore_index=True)

    # Add the video URLs to the tweet DataFrame
    df_tweets['video_urls'] = video_urls
                 
    # Save the DataFrames as CSV files (optional)
    df_tweets.to_csv('tweets.csv', index=False)

    # Create a directory to save video files
    video_dir = '/Users/stella/Documents/video_scraping_floods2023'
    os.makedirs(video_dir, exist_ok=True)
    
    # Download and save video files
    for index, video_url in enumerate(video_urls):
        if video_url:
            response = requests.get(video_url)
            if response.status_code == 200:
                filename = f"{index + 1}.mp4"
                with open(os.path.join(video_dir, filename), 'wb') as video_file:
                    video_file.write(response.content)
                print(f"Downloaded and saved video: {filename}")
            else:
                print(f"Failed to download video for URL: {video_url}")
        else:
            print(f"No video URL for row {index + 1}.")
    
    print("Video files downloaded and saved in 'video_files' directory.")
else:
    # Print an error message if the request failed
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
    
