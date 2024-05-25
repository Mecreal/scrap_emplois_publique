import requests
from bs4 import BeautifulSoup
import html
import json
import schedule
import time

JSON_FILE = 'something.json'

def get_html_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def parse_table(html_content):
    decoded_html = html.unescape(html_content)
    soup = BeautifulSoup(decoded_html, 'html.parser')
    table = soup.find(class_='table-responsive')

    if not table:
        return None

    headers = [header.get_text(separator=" ").strip() for header in table.find_all('th')]

    rows = []
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        row_data = {}
        for i, cell in enumerate(cells):
            row_data[headers[i]] = cell.get_text(separator=" ").strip()
        rows.append(row_data)
        
    return rows

def load_existing_data():
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_data(data):
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def update_data():
    all_rows = load_existing_data()
    existing_ids = {row['Grade'] for row in all_rows}

    new_data_found = False
    for page_number in range(1, 46):
        url = f"https://www.emploi-public.ma/fr/concoursListe.asp?c=0&e=1&p={page_number}"
        html_content = get_html_content(url)

        if html_content:
            rows = parse_table(html_content)
            if rows:
                new_rows = [row for row in rows if row['Grade'] not in existing_ids]
                if new_rows:
                    all_rows.extend(new_rows)
                    existing_ids.update(row['Grade'] for row in new_rows)
                    new_data_found = True
            else:
                print(f"No table found on page {page_number}.")
        else:
            print(f"Failed to retrieve content from page {page_number}.")

    if new_data_found:
        save_data(all_rows)
        print("Data has been updated and saved to something.json")
    else:
        print("No new data found.")

# Schedule the update_data function to run every 6 hours
schedule.every(6).hours.do(update_data)

print("Scheduler started. Updating data every 6 hours.")
update_data()  # Initial run

while True:
    schedule.run_pending()
    time.sleep(1)
