"""This module is responsible for searching the web for relevant URLs."""

import requests
import time
from utils.utils import SocialNetwork
import utils.utils as utils
from dotenv import load_dotenv
from googlesearch import search


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
                print(search_results)
                time.sleep(5)
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


def search_with_gs(query: str, social_network: SocialNetwork) -> str:
    """Searches Google for the query and returns the first relevant URL."""
    for result in search(query, num_results=5, lang='pt-br', sleep_interval=5):
        if social_network.is_valid_link(result):
            return result

def main():
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    data_posts = utils.read_posts(file_name)
    
    # Converter a coluna de URLs para string
    url_column = social_network.get_post_url_column()
    data_posts[url_column] = data_posts[url_column].astype(str)
    
    for index, row in data_posts.iterrows():
        text = row['message']
        text = utils.filter_bmp_characters(text)
        
        query = social_network.generate_query(text, row['username'])
        post_url = search_with_gs(query, social_network)
       
        if post_url:
            post_url = utils.extract_relevant_url(post_url)
            data_posts.at[index, social_network.get_post_url_column()] = post_url
            print(f"URL encontrada para a linha {index + 2}: {post_url:}")
        else:
            print(f"URL não encontrada para a linha {index + 2}")
            data_posts.drop(index, inplace=True) #remover a linha

            
        # google_ofc_searcher = Searcher(
        #     cse_id=utils.env_variable("CSE_ID"),
        #     num_keys=int(utils.env_variable("NUM_KEYS"))
        # )   
         
        # post_url = google_ofc_searcher.start_search(
        #     query=query,
        #     social_network=social_network,
        #     max_results=10
        # )
        
        # if post_url:
        #     post_url = utils.extract_relevant_url(post_url)
        #     data_posts.at[index, social_network.get_post_url_column()] = post_url
        #     print(f"URL encontrada para a linha {index + 2}: {post_url:}")
        # else:
            # print(f"URL não encontrada para a linha {index + 2}")
            # #remover linha
            # data_posts.drop(index, inplace=True)
             
    json_data_posts = utils.format_data(data_posts, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_data_posts, f'{file_name[:-4]}.json')
    
if __name__ == '__main__':
    load_dotenv()
    main()