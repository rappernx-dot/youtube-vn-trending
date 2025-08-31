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

    # Extract chart date from page title
    title_span = soup.find("span", class_="pagetitle")
    chart_title = title_span.find("strong").text if title_span else "YouTube Vietnam Daily Chart"
    chart_date = chart_title.split("-")[1].strip().split(" |")[0] if len(chart_title.split("-")) > 1 else "Unknown"

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
        streams_change = cols[4].text.strip().replace(",", "")  # Keep as is, including sign or empty
        
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
