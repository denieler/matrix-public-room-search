import requests
from bs4 import BeautifulSoup

# URL of the web page to scrape
url = "https://tatsumoto-ren.github.io/matrix/"

try:
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
except requests.exceptions.RequestException as e:
    print(f"Error fetching the web page: {e}")
    exit(1)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.text, 'html.parser')

# Find the div with class "servers"
servers_div = soup.find('div', class_='servers')

if not servers_div:
    print("No div with class 'servers' found.")
    exit(1)

# Find the div with id "blocklist" within servers_div
blocklist_div = servers_div.find('div', id='blocklist')

# Initialize a list to collect input elements
inputs = []

if blocklist_div:
    # Collect all elements before blocklist_div within servers_div
    elements_before_blocklist = []
    for element in servers_div.contents:
        if element == blocklist_div:
            break
        elements_before_blocklist.append(element)
    
    # Create a new BeautifulSoup object from the elements before blocklist_div
    pre_blocklist_soup = BeautifulSoup(''.join(str(e) for e in elements_before_blocklist), 'html.parser')
    
    # Find input elements within the new soup
    inputs = pre_blocklist_soup.find_all('input', {'type': 'text', 'class': 'host'})
else:
    # If blocklist_div is not found, process all inputs within servers_div
    inputs = servers_div.find_all('input', {'type': 'text', 'class': 'host'})

# Extract the 'value' attribute from each input element
values = [inp.get('value') for inp in inputs if inp.get('value')]

# Write the values to 'servers.txt', one per line
try:
    with open('servers.txt', 'w') as file:
        for val in values:
            file.write(f"{val}\n")
    print("Servers have been written to servers.txt")
except IOError as e:
    print(f"Error writing to file: {e}")
