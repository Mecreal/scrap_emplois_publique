import requests
from bs4 import BeautifulSoup
import html
from datetime import datetime
from data_handler import load_existing_data, save_data, reassign_ids

URL_PREFIX = 'https://www.emploi-public.ma/fr/'

# Try setting the locale to French
try:
    import locale
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
except locale.Error:
    print("French locale not supported. Falling back to default locale.")
    locale.setlocale(locale.LC_TIME, '')

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
        return []

    headers = [header.get_text(separator=" ").strip() for header in table.find_all('th')]
    headers.insert(0, "unique_id")  # Insert "unique_id" header at the beginning

    rows = []
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        row_data = {}
        for i, cell in enumerate(cells):
            if cell.find('a'):
                link = cell.find('a')['href']
                unique_id = link.split('id=')[-1]
                row_data['unique_id'] = unique_id
                row_data[headers[i + 1]] = {
                    'text': cell.get_text(separator=" ").strip(),
                    'link': URL_PREFIX + link
                }
            else:
                row_data[headers[i + 1]] = cell.get_text(separator=" ").strip()

            # Parse the date fields and store them in a comparable format
            if headers[i + 1] == 'Date publication':
                date_str = cell.get_text(separator=" ").strip()
                try:
                    row_data['date_publication'] = datetime.strptime(date_str, '%d %B %Y') if date_str else None
                except ValueError:
                    row_data['date_publication'] = None

        rows.append(row_data)
        
    return rows

def update_data():
    all_rows = load_existing_data()
    existing_ids = {row['unique_id'] for row in all_rows}

    new_rows = []
    for page_number in range(1, 46):  # Adjust the range as needed
        url = f"https://www.emploi-public.ma/fr/concoursListe.asp?c=0&e=1&p={page_number}"
        html_content = get_html_content(url)

        if html_content:
            rows = parse_table(html_content)
            if rows:
                # Add new rows to new_rows list if not already in existing data
                for row in rows:
                    if row['unique_id'] not in existing_ids:
                        new_rows.append(row)
                        existing_ids.add(row['unique_id'])
            else:
                print(f"No table found on page {page_number}.")
        else:
            print(f"Failed to retrieve content from page {page_number}.")

    if new_rows:
        all_rows.extend(new_rows)
        all_rows = reassign_ids(all_rows)

        # Sort the rows by 'date_publication' in descending order, treating None as the oldest
        all_rows.sort(key=lambda x: (x['date_publication'] is not None, x['date_publication']), reverse=True)

        save_data(all_rows)
        print("Data has been updated and saved to something.json")
    else:
        print("No new data found.")
