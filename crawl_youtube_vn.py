import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# URL of the YouTube Vietnam Daily Chart
url = "https://kworb.net/youtube/insights/vn_daily.html"

try:
    # Send a GET request with headers to ensure proper encoding
    headers = {'Accept-Language': 'en-US,en;q=0.9', 'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, timeout=10, headers=headers)
    response.raise_for_status()  # Raise error if request fails
    response.encoding = 'utf-8'  # Force UTF-8 encoding
    soup = BeautifulSoup(response.text, "html.parser", from_encoding="utf-8")

    # Extract chart date from page title (e.g., "YouTube Vietnam Daily Chart - 2025/08/28 | Weekly")
    title_span = soup.find("span", class_="pagetitle")
    chart_title = title_span.find("strong").text if title_span else "YouTube Vietnam Daily Chart"
    chart_date_raw = chart_title.split("-")[1].strip().split(" |")[0] if len(chart_title.split("-")) > 1 else "Unknown"
    # Convert date to a readable format (e.g., "28 August 2025")
    try:
        chart_date = datetime.strptime(chart_date_raw, "%Y/%m/%d").strftime("%d %B %Y")
    except ValueError:
        chart_date = chart_date_raw  # Fallback if date parsing fails

    # Extract note (e.g., "Showing streams in the past two days.")
    note_element = title_span.next_sibling.next_sibling  # Assuming structure: <br><br>Showing...<br><br>
    note = note_element.strip() if note_element and "Showing" in note_element else "Showing streams in the past two days."

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
        streams_change = cols[4].text.strip().replace(",", "") if cols[4].text.strip() else ""

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
            "chart_date": chart_date,
            "last_updated": response.headers.get("Date", "Unknown"),
            "note": note,
            "data": chart_data
        }, f, ensure_ascii=False, indent=2)

    print("Data crawled and saved to youtube_vn_daily.json")
except Exception as e:
    print(f"Error during crawl: {e}")
    # Optionally, keep old data or notify
