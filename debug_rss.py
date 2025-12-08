import requests
import xml.etree.ElementTree as ET
import json

def check_url(url, is_xml=True):
    print(f"\nChecking: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/xml,application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Cookie": "NID=..." # Sometimes needed, but leaving empty for now
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            if is_xml:
                 try:
                     root = ET.fromstring(response.content)
                     items = root.findall(".//item")
                     print(f"RSS Items found: {len(items)}")
                 except:
                     print("Failed to parse XML")
            else:
                 try:
                     data = json.loads(response.content[5:]) # Google JSON often has prefix
                     print("JSON parsed successfully")
                 except:
                     try:
                        data = json.loads(response.content)
                        print("JSON parsed successfully")
                     except:
                        print("Failed to parse JSON")
        else:
            print("Failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    urls = [
        ("https://trends.google.com/trends/trendingsearches/daily/rss?geo=US", True),
        ("https://trends.google.com/trending/rss?geo=US", True),
        ("https://trends.google.com/trends/api/dailytrends?hl=en-US&tz=420&geo=US&ns=15", False),
    ]
    for url, is_xml in urls:
        check_url(url, is_xml)
