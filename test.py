import requests
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures
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
    url = 'https://www.pinkvilla.com/entertainment/movie-review'
    soup = scrape_with_scraperapi(url, {'country_code': "in"})
    
    urls = []
    info = {}
    
    # Extracting the name and URL from the soup
    for a_tag in soup.find_all('a', href=True, title=True):
        title = a_tag.get('title')
        href = a_tag.get('href')
        
        # Check if the title contains the word "Review"
        if 'Review' in title:
            urls.append(href)
            info[href] = title
    
    return urls
def scrape_individual_page(url):
    
    # url = "https://www.pinkvilla.com/entertainment/reviews/munjya-review-sharvari-wagh-and-abhay-vermas-movie-is-quite-literally-a-horror-show-after-a-promising-start-1314092"
    soup = scrape_with_scraperapi(url)
    
    # Extract the title
    title_tag = soup.find('h1', class_='beebom-single-heading')
    title = title_tag.get_text(strip=True) if title_tag else 'No title found'
    
    # Extract the main content from <div class="row">
    content_div = soup.find('div', class_='row')
    content = []
    if content_div:
        for child in content_div.children:
            if isinstance(child, str) or (child.name != 'div' or ('tags-section' not in child.get('class', []) and 'recommended-articles-section' not in child.get('class', []))):
                text = child.get_text() if hasattr(child, 'get_text') else str(child)
                text = text.replace('\t', ' ').replace('\n', ' ')
                content.append(text)
            else:
                break
    
    # Extract key highlights from <div class="key_hlts_art_23" id="key_highlight">
    key_highlights_div = soup.find('div', class_='key_hlts_art_23', id='key_highlight')
    if key_highlights_div:
        for child in key_highlights_div.children:
            text = child.get_text(strip=True) if hasattr(child, 'get_text') else str(child)
            text = text.replace('\t', ' ').replace('\n', ' ')
            content.append(text)
    
    return {
        'url': url,
        'title': title,
        'content': ' '.join(content)
    }


urls = scrape_news()

data = []
for url in urls:
    page_data = scrape_individual_page(url)
    data.append(page_data)

# Write data to JSON file
with open('scraped_data_movies.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)