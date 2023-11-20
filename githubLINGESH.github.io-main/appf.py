import html
from flask import Flask, render_template, request
from googleapiclient.discovery import build

app = Flask(__name__)

# Route for the home page
@app.route('/')
def home():
    return render_template('front.html')

@app.route('/report')
def report():
    return render_template('report.html')

# Route for the fake_news_finder page
@app.route('/fake_news_finder', methods=['GET', 'POST'])
def fake_news_finder():
    if request.method == 'POST':
        # Get the keyword and rate limit from the form
        keyword = request.form['keyword']
        rate_limit = int(request.form['rate_limit'])
        
        api_key = "YOUR_YOUTUBE_API_KEY"  # Replace with your actual YouTube API key
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Search YouTube for videos with the keyword
        search_response = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            maxResults=rate_limit
        ).execute()

        videos = []
        for item in search_response["items"]:
            video_title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            channel_title = item["snippet"]["channelTitle"]
            published_at = item["snippet"]["publishedAt"]

            # Retrieve video details
            video_response = youtube.videos().list(
                part="statistics",
                id=video_id
            ).execute()

            view_count = video_response["items"][0]["statistics"].get("viewCount", 0)
            like_count = video_response["items"][0]["statistics"].get("likeCount", 0)

            videos.append({
                'video_title': video_title,
                'video_id': video_id,
                'channel_title': channel_title,
                'published_at': published_at,
                'view_count': view_count,
                'like_count': like_count
            })

        # Retrieve keyword-related comments
        comments = []
        for video in videos:
            video_id = video['video_id']
            comment_response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                searchTerms=keyword,
                maxResults=rate_limit
            ).execute()

            if "items" in comment_response:
                for comment in comment_response["items"]:
                    comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
                    comment_text = html.unescape(comment_text)
                    comments.append(comment_text)

        response = f"Response from the modified code. Keyword: {keyword}"

        return render_template('fake_news_finder.html', videos=videos, comments=comments, response=response)

    return render_template('fake_news_finder.html', videos=None, comments=None, response=None)

# Route for the working page
@app.route('/working/')
def working():
    return render_template('working.html')

# Route for the privacy policy page
@app.route('/privacy_policy/')
def privacy_policy():
    return render_template('privacy_policy.html')
    
# Define the route to handle form submissions
@app.route('/report', methods=['POST'])
def report_user():
    if request.method == 'POST':
        # Get the submitted report user
        report_user = request.form.get('reportUser')

        # Save the report user to a file (you can use any format you prefer)
        with open('report_users.txt', 'a') as file:
            file.write(report_user + '\n')

        return "Report submitted successfully."

if __name__ == '__main__':
    app.run(debug=True)
