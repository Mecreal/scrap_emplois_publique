import aiohttp
import asyncio
from bs4 import BeautifulSoup
import html
from datetime import datetime
from data_handler import load_existing_data, save_data, reassign_ids

URL_PREFIX = 'https://www.emploi-public.ma/fr/'
max_pages = 500
consecutive_failures = 0
MAX_CONSECUTIVE_FAILURES = 5

# Try setting the locale to French
def set_locale():
    try:
        import locale
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
        return True
    except locale.Error:
        print("French locale not supported. Falling back to default locale.")
        return False

FRENCH_LOCALE_SUPPORTED = set_locale()

# Custom date parser for French dates
def parse_french_date(date_str):
    if not date_str:
        return None
    months = {
        "janvier": "January", "février": "February", "mars": "March", "avril": "April",
        "mai": "May", "juin": "June", "juillet": "July", "août": "August",
        "septembre": "September", "octobre": "October", "novembre": "November", "décembre": "December"
    }
    for fr, en in months.items():
        date_str = date_str.replace(fr, en)
    try:
        return datetime.strptime(date_str, '%d %B %Y')
    except ValueError:
        return None

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def fetch_all(session, urls):
    tasks = []
    for url in urls:
        tasks.append(fetch(session, url))
    return await asyncio.gather(*tasks)

async def get_html_content_async(urls):
    async with aiohttp.ClientSession() as session:
        html_contents = await fetch_all(session, urls)
    return html_contents

def parse_table(html_content):
    decoded_html = html.unescape(html_content)
    soup = BeautifulSoup(decoded_html, 'html.parser')
    table = soup.find(class_='table-responsive')

    if not table:
        return []

    headers = [header.get_text(separator=" ").strip() for header in table.find_all('th')]
    headers.insert(0, "unique_id")

    rows = []
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        row_data = {}
        unique_id = None

        for i, cell in enumerate(cells):
            if i == 1 and cell.find('a'):
                link = cell.find('a')['href']
                unique_id = link.split('id=')[-1]
                row_data['Grade'] = {
                    'text': cell.get_text(separator=" ").strip(),
                    'link': URL_PREFIX + link
                }
            elif cell.find('a'):
                link = cell.find('a')['href']
                row_data[headers[i + 1]] = {
                    'text': cell.get_text(separator=" ").strip(),
                    'link': URL_PREFIX + link
                }
            else:
                row_data[headers[i + 1]] = cell.get_text(separator=" ").strip()

            if headers[i + 1] == 'Date publication':
                date_str = cell.get_text(separator=" ").strip()
                row_data['date_publication'] = parse_french_date(date_str)

        if unique_id:
            row_data['unique_id'] = unique_id
        row_data['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        rows.append(row_data)

    return rows

def update_data():
    global consecutive_failures

    all_rows = load_existing_data()
    if 'data' not in all_rows:
        print("Error: Loaded data does not contain 'data' key.")
        return

    existing_ids = {row['unique_id'] for row in all_rows['data']}
    existing_data_dict = {row['unique_id']: row for row in all_rows['data']}
    new_rows = []

    urls = [f"https://www.emploi-public.ma/fr/concoursListe.asp?c=0&e=1&p={page_number}" for page_number in range(1, max_pages + 1)]
    
    html_contents = asyncio.run(get_html_content_async(urls))

    for html_content in html_contents:
        if html_content:
            rows = parse_table(html_content)
            if rows:
                for row in rows:
                    unique_id = row['unique_id']
                    if unique_id not in existing_ids:
                        new_rows.append(row)
                        existing_ids.add(unique_id)
                        existing_data_dict[unique_id] = row
                    else:
                        print(f"Already fetched page with unique_id {unique_id}. Stopping.")
                        break  # Stop fetching more pages
            else:
                print(f"No table found in the HTML content.")
        else:
            print(f"Failed to retrieve content.")

    if new_rows:
        all_rows['data'] = reassign_ids(list(existing_data_dict.values()))
        # Sort the rows by 'date_publication' in descending order, handling None values properly
        all_rows['data'].sort(
            key=lambda x: (x['date_publication'] is not None, x['date_publication'].strftime('%Y-%m-%d') if isinstance(x['date_publication'], datetime) else x['date_publication']), 
            reverse=True
        )

        all_rows['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for row in all_rows['data']:
            if isinstance(row.get('date_publication'), datetime):
                row['date_publication'] = row['date_publication'].strftime('%Y-%m-%d')
            if isinstance(row.get('last_updated'), datetime):
                row['last_updated'] = row['last_updated'].strftime('%Y-%m-%d %H:%M:%S')

        save_data(all_rows)
        print("Data has been updated and saved to something.json")
    else:
        print("No new data found.")

if __name__ == "__main__":
    update_data()
