import requests
from bs4 import BeautifulSoup
import html
import json

def get_html_content(url):
    """Fetches the HTML content of a given URL.

    Args:
        url (str): The URL of the website.

    Returns:
        str: The HTML content of the website, or None if an error occurred.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404)
        response.encoding = 'utf-8'  # Ensure the response is decoded using utf-8
        return response.text  # Get the HTML content as text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None

def parse_table(html_content):
    """Parses the table content from the HTML.

    Args:
        html_content (str): The HTML content of the page.

    Returns:
        list: A list of dictionaries representing the table rows.
    """
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

# Initialize an empty list to store all rows
all_rows = []

# Loop over the pages
for page_number in range(1, 200):  # Adjust the range as needed
    url = f"https://www.emploi-public.ma/fr/concoursListe.asp?c=0&e=1&p={page_number}"
    html_content = get_html_content(url)

    if html_content:
        rows = parse_table(html_content)
        if rows:
            all_rows.extend(rows)
        else:
            print(f"No table found on page {page_number}.")
    else:
        print(f"Failed to retrieve content from page {page_number}.")

# Write the accumulated rows to a JSON file
if all_rows:
    with open('something.json', 'w', encoding='utf-8') as f:
        json.dump(all_rows, f, ensure_ascii=False, indent=4)
    print("Data has been saved to something.json")
else:
    print("No data was scraped.")
