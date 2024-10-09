"""Obtém URLs dos posts"""

from enum import Enum
import requests
import time
from utils.utils import SocialNetwork
import utils.utils as utils
import random
from bs4 import BeautifulSoup


class Searcher:
    CSE_API_URL = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, cse_id: str, num_keys: int):
        self.cse_id = cse_id
        self.keys = []
        
        for key in range(num_keys):
            self.keys.append([utils.env_variable(f"CSE_API_KEY_{key}"), 0, True])

    def start_search(self, query: str, social_network: SocialNetwork, max_results: int) -> str:
        """Searches Google for the query and returns the first relevant URL."""
        
        for attempt in range(len(self.keys)):
            if not self.keys[attempt][2] or self.keys[attempt][1] > 100:  # Se chave estiver desativada or ter atingido 100 requisições, pule para a próxima
                continue
            
            params = {
                'q': query,
                'key': self.keys[attempt][0],
                'cx': self.cse_id,
                'num': max_results
            }
            try:
                response = requests.get(self.CSE_API_URL, params=params)
                response.raise_for_status()
                search_results = response.json()
                self.keys[attempt][1] += 1
                
                items = search_results.get('items', [])
                for item in items:
                    link = item['link']
                    if social_network.is_valid_link(link):
                        return link
                return ''
            
            except requests.exceptions.HTTPError as e:
                if response.status_code == 429:
                    # Acabou a cota da api
                    self.keys[attempt][2] = False
                else:
                    print(f"Erro na requisição: {e}")
        return ''
            
            
            
class SearchEngineAlternatives(Enum):
    """The search engines used to search for the posts."""
    BING = "https://www.bing.com/search?q="
    DUCKDUCKGO =  "https://duckduckgo.com/html/?q="
    
    def get_url(self) -> str:
        return self.value
    

def search_alternative(query: str, social_network: SocialNetwork):
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.48",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
    }
    
    search_engines = [(engine.get_url() + query)
                      for engine in SearchEngineAlternatives]

    for search_url in search_engines:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        for link in soup.find_all('a', href=True):
            href = link['href']
            if social_network.is_valid_link(href):
                return href
            return ''
        time.sleep(random.uniform(1, 3))
    return ''


def main():
    google_ofc_searcher = Searcher(
        cse_id=utils.env_variable("CSE_ID"),
        num_keys=utils.env_variable("NUM_KEYS")
    )
    
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    data_posts = utils.read_posts(file_name)
    
    for index, row in data_posts.iterrows():
        text = row['message']
        query = utils.filter_bmp_characters(text)
        
        post_url = google_ofc_searcher.start_search(
            query=query,
            social_network=social_network,
            max_results=10
        )
        
        if post_url:
            post_url = utils.extract_relevant_url(post_url)
            data_posts.at[index, social_network.get_post_url_column()] = post_url
            print(f"URL encontrada para a linha {index + 1}: {post_url:}")
        else:
            new_query = social_network.generate_alternative_query(query)
            post_url = search_alternative(new_query, social_network)
            if post_url:
                post_url = utils.extract_relevant_url(post_url)
                data_posts.at[index, social_network.get_post_url_column()] = post_url
                print(f"URL encontrada para a linha {index + 1} de forma alternativa: {post_url:}")     
            else:
                print(f"URL não encontrada para a linha {index + 1}")
             
    data_posts.to_csv(f'{file_name[:-4]}_with_urls.csv', index=False)
    json_data_posts = utils.format_data(data_posts, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_data_posts, f'{file_name[:-4]}.json')
    