"""This module is responsible for searching the web for relevant URLs."""

from social_network.social_network import SocialNetwork
from utils import utils
from dotenv import load_dotenv
from googlesearch import search
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import random
import requests
import time

CSE_ID = None
gs_active = True

class CSEKey:
    def __init__(self, key: str):
        self.key = key
        self.num_requests = 0
        self.is_active = True

    def increment_requests(self):
        self.num_requests += 1
        if self.num_requests > 100:
            self.is_active = False

class CSEKeyManager:
    def __init__(self, keys: list[str]):
        self.keys = [CSEKey(key) for key in keys]
        self.success_searches = 0

    def get_active_key(self):
        for key in self.keys:
            if key.is_active:
                return key
        return None

    def search_post(self, query: str, social_network: SocialNetwork) -> str:
        """Searches Google for the query and returns the first relevant URL."""
        while True:
            key = self.get_active_key()
            if not key:
                print("All CSE keys have reached the request limit.")
                return ''
            
            service = build("customsearch", "v1", developerKey=key.key)
            key.increment_requests()
            
            try:
                response = service.cse().list(q=query, cx=CSE_ID).execute()
                if 'items' in response:
                    for item in response['items']:
                        link = item['link']
                        if social_network.is_valid_link(link):
                            self.success_searches += 1
                            return link
                return ''
            except HttpError as e:
                if e.resp.status == 429:
                    print(f"Key {key.key} reached the request limit. Deactivating key.")
                    key.is_active = False
                else:
                    print(f"Request error: {e}")
                    return '' 

class SEAlternativesManager:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]

    def __init__(self, searches_urls: list[str]):
        self.searches_urls = searches_urls
        self.search_success = 0
        
    def make_request(self, query: str, social_network: SocialNetwork) -> str:
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        
        for url in self.searches_urls:
            try:
                response = requests.get(url + query, headers=headers, timeout=10)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(f"Request error: {e}")
                return ''
            except Exception as e:
                print(f"Request error: {e}")
                return ''
                
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if social_network.is_valid_link(href):
                    self.search_success += 1
                    return href
            
            time.sleep(random.uniform(1, 3))
        return ''

def search_with_gs(query: str, social_network: SocialNetwork) -> str:
    """Searches Google for the query and returns the first relevant URL."""
    global gs_active
    try:
        results = search(query, num_results=5, lang='pt-br', sleep_interval=5)
        for link in results:
            if social_network.is_valid_link(link):
                return link
        return ''
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("GS request limit reached. Deactivating GS.")
            gs_active = False
            return ''
        else:
            print(f"Request error: {e}")
            return ''
    except Exception as e:
        print(f"Request error: {e}")
        return ''

def search_with_all_engines(query: str, social_network: SocialNetwork, cse: CSEKeyManager, alt: SEAlternativesManager) -> str:
    """Try searching using all available mechanisms."""
    post_url = cse.search_post(query, social_network)
    if not post_url:
        post_url = alt.make_request(query, social_network)
    if not post_url and gs_active:
        post_url = search_with_gs(query, social_network)
    return post_url or ''

def process_search(query: str, social_network: SocialNetwork, cse: CSEKeyManager, alt: SEAlternativesManager) -> str:
    """Process the search and return the relevant URL."""
    post_url = search_with_all_engines(query, social_network, cse, alt)
    return utils.extract_relevant_url(post_url)

def main():
    load_dotenv()
    global CSE_ID
    CSE_ID = utils.env_variable("CSE_ID")
    cse_keys = utils.get_cse_keys(int(utils.env_variable("NUM_KEYS")))
    key_manager = CSEKeyManager(cse_keys)
    
    alt_search_engines = SEAlternativesManager([
        "https://www.bing.com/search?q=",
        "https://duckduckgo.com/html/?q="
    ])
    
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    data_posts = utils.read_posts(file_name)
    posts_without_url = data_posts.copy(deep=True)
    
    for index, row in data_posts.iterrows():
        text = row['message']
        text = utils.filter_bmp_characters(text)
        query = social_network.generate_query(text, row['username'])
        post_url = process_search(query, social_network, key_manager, alt_search_engines)
        
        if post_url:
            data_posts.at[index, social_network.get_post_url_column()] = post_url
            print(f"URL found for row {index + 2}: {post_url}")
            posts_without_url.drop(index, inplace=True)
        else:
            print(f"URL not found for row {index + 2}")
            data_posts.drop(index, inplace=True)
        
    data_posts.to_csv(f'{file_name[:-4]}_com_url.csv', index=False)
    posts_without_url.to_csv(f'{file_name[:-4]}_sem_url.csv', index=False)
                
    json_data_posts = utils.format_data(data_posts, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_data_posts, f'{file_name[:-4]}.json')

    print(f"\nTotal posts: {len(data_posts)}")
    print(f"Total posts without URL: {len(posts_without_url)}")

if __name__ == '__main__':
    main()