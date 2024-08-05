import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import json
import time

load_dotenv()

API_KEY = os.getenv('APIKEY')
BASE_URL = 'http://api.scraperapi.com'

def scrape_with_scraperapi(url, params=None):
    """
    Generic function to scrape a URL using ScraperAPI.
    
    :param url: The URL to scrape
    :param params: Additional parameters for ScraperAPI
    :return: BeautifulSoup object of the scraped content
    """
    default_params = {
        'api_key': API_KEY,
        'url': url,
    }
    if params:
        default_params.update(params)
    # print(default_params)
    response = requests.get(BASE_URL, params=default_params)
    return BeautifulSoup(response.text, 'html.parser')

def scrape_news():
    url = 'https://beebom.com/category/tech/'
    soup = scrape_with_scraperapi(url, {'country_code': "in"})
    
    urls = []
    # Extracting the name and URL from the soup
    info = {}
    for entry in soup.find_all('div', class_='entry-wrapper'):
        a_tag = entry.find('a', class_='u-url')
        if a_tag:
            name = a_tag.get('title')
            url = a_tag.get('href')
            urls.append(url)
            info[url] = name
    
    return urls

def scrape_individual_page(url):
    # url="https://beebom.com/nothing-phone-2a-plus-review/"
    soup = scrape_with_scraperapi(url)
    # Extract the title
    title_tag = soup.find('h1', class_='beebom-single-heading')
    title = title_tag.get_text(strip=True) if title_tag else 'No title found'
    
    # Extract the content until the tags-section
    content_div = soup.find('div', class_='beebom-single-content entry-content highlight')
    content = []
    if content_div:
        for child in content_div.children:
            if isinstance(child, str) or (child.name != 'div' or ('tags-section' not in child.get('class', []) and 'recommended-articles-section' not in child.get('class', []))):
                text = child.get_text() if hasattr(child, 'get_text') else str(child)
                text = text.replace('\t', ' ').replace('\n', ' ')
                content.append(text)
            else:
                break
    
    return {
        'url': url,
        'title': title,
        'content': ' '.join(content)
    }


urls = scrape_news()
data = []
for index, url in enumerate(urls):
    page_data = scrape_individual_page(url)
    data.append(page_data)
    print(f"Scraped URL: {url}")
    print(f"Pages left: {len(urls) - index - 1}")

# Write data to JSON file
with open('scraped_data_tech.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)