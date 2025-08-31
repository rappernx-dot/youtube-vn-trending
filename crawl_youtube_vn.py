import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import urllib.parse
import time

# YouTube Data API key (set in GitHub Actions secrets)
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
if not YOUTUBE_API_KEY:
    print("Error: YOUTUBE_API_KEY environment variable not set")

# URL of the YouTube Vietnam Daily Chart
url = "https://kworb.net/youtube/insights/vn_daily.html"

try:
    # Send a GET request with headers to ensure proper encoding
    headers = {
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print("Fetching chart data from:", url)
    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract chart date
    title_span = soup.find("span", class_="pagetitle")
    chart_title = title_span.find("strong").text if title_span else "YouTube Vietnam Daily Chart"
    chart_date_raw = chart_title.split("-")[1].strip().split(" |")[0] if len(chart_title.split("-")) > 1 else "Unknown"
    try:
        chart_date = datetime.strptime(chart_date_raw, "%Y/%m/%d").strftime("%d/%m/%Y")
        print(f"Chart date parsed: {chart_date}")
    except ValueError:
        chart_date = chart_date_raw
        print(f"Chart date fallback: {chart_date}")

    # Extract note
    note_element = title_span.next_sibling.next_sibling
    note = note_element.strip() if note_element and "Showing" in note_element else "Hiển thị lượt nghe trong hai ngày qua."
    print(f"Note extracted: {note}")

    # Find the table
    table = soup.find("table", id="dailytable")
    if not table:
        raise ValueError("Table with id='dailytable' not found")
    
    # Initialize chart data
    chart_data = []
    rows = table.find("tbody").find_all("tr")
    print(f"Found {len(rows)} rows in the chart table")
    for row in rows:
        cols = row.find_all("td")
        position = cols[0].text.strip()
        position_change = cols[1].text.strip()
        track = cols[2].text.strip()
        streams = cols[3].text.strip().replace(",", "")
        streams_change = cols[4].text.strip().replace(",", "") if cols[4].text.strip() else ""
        print(f"Extracted track: {track} (Position: {position})")
        chart_data.append({
            "position": position,
            "position_change": position_change,
            "track": track,
            "streams": streams,
            "streams_change": streams_change,
            "youtube_link": "",
            "affiliate_link": ""
        })

    # Search YouTube using API
    for item in chart_data:
        query = urllib.parse.quote(item['track'])
        print(f"Searching YouTube API for: {item['track']} (Encoded query: {query})")
        try:
            api_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=video&maxResults=1&key={YOUTUBE_API_KEY}"
            print(f"API request URL: {api_url}")
            api_response = requests.get(api_url, timeout=10)
            print(f"YouTube API status code: {api_response.status_code}")
            if api_response.status_code != 200:
                print(f"API error response: {api_response.text}")
                continue
            data = api_response.json()
            if data.get('items'):
                video_id = data['items'][0]['id']['videoId']
                item['youtube_link'] = f"https://www.youtube.com/watch?v={video_id}"
                print(f"Found YouTube link: {item['youtube_link']}")
            else:
                print(f"No video found for: {item['track']}")
            # Placeholder for affiliate link
            # Example: item['affiliate_link'] = f"https://example.com/aff?track={urllib.parse.quote(item['track'])}"
            print(f"Affiliate link (placeholder): {item['affiliate_link']}")
            time.sleep(0.5)  # Delay to respect API rate limits
        except Exception as e:
            print(f"Error searching YouTube API for '{item['track']}': {str(e)}")

    # Save the data to a JSON file
    with open("youtube_vn_daily.json", "w", encoding="utf-8") as f:
        json.dump({
            "chart_date": chart_date,
            "last_updated": response.headers.get("Date", "Unknown"),
            "note": note,
            "data": chart_data
        }, f, ensure_ascii=False, indent=2)

    print("Data crawled and saved to youtube_vn_daily.json")
except Exception as e:
    print(f"Error during crawl: {str(e)}")
