import requests
from bs4 import BeautifulSoup
import json
import os

# URL of the YouTube Vietnam Daily Chart
url = "https://kworb.net/youtube/insights/vn_daily.html"

try:
    # Send a GET request to fetch the page content
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise error if request fails
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table with id="dailytable"
    table = soup.find("table", id="dailytable")

    # Initialize a list to store the chart data
    chart_data = []

    # Extract table rows (skip the header)
    rows = table.find("tbody").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        # Extract data from each column
        position = cols[0].text.strip()
        position_change = cols[1].text.strip()
        track = cols[2].text.strip()
        streams = cols[3].text.strip().replace(",", "")
        streams_change = cols[4].text.strip().replace(",", "") if cols[4].text.strip() else "0"
        
        # Append to chart_data
        chart_data.append({
            "position": position,
            "position_change": position_change,
            "track": track,
            "streams": streams,
            "streams_change": streams_change
        })

    # Save the data to a JSON file
    with open("youtube_vn_daily.json", "w", encoding="utf-8") as f:
        json.dump({
            "last_updated": response.headers.get("Date", "Unknown"),
            "data": chart_data
        }, f, ensure_ascii=False, indent=2)

    print("Data crawled and saved to youtube_vn_daily.json")
except Exception as e:
    print(f"Error during crawl: {e}")
    # Optionally, keep old data or notify
