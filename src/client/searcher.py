"""This module is responsible for searching the web for relevant URLs."""

from social_network.social_network import SocialNetwork
from utils import utils
from dotenv import load_dotenv
from googlesearch import search
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

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
                print("Todas as chaves atingiram o limite de requisições. Desativando CSE.")
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
                    print(f"Key {key.key} atingiu o limite de requisições. Desativando chave...")
                    key.is_active = False
                else:
                    print(f"Request error: {e}")
                    return '' 


def search_with_gs_lib(query: str, social_network: SocialNetwork) -> str:
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
            print("Google Search atingiu o limite de requisições. Desativando GS.")
            gs_active = False
            return ''
        else:
            print(f"Erro na requisição: {e}")
            return ''
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return ''


def search_with_all_engines(query: str, social_network: SocialNetwork, cse: CSEKeyManager) -> str:
    """Try searching using all available mechanisms."""
    post_url = cse.search_post(query, social_network)

    if not post_url and gs_active:
        post_url = search_with_gs_lib(query, social_network)
        
    return post_url or ''


def process_search(query: str, social_network: SocialNetwork, cse: CSEKeyManager) -> str:
    """Process the search and return the relevant URL."""
    post_url = search_with_all_engines(query, social_network, cse)
    return utils.extract_relevant_url(post_url)


def main():
    load_dotenv()
    global CSE_ID
    CSE_ID = utils.env_variable("CSE_ID")
    cse_keys = utils.get_cse_keys(int(utils.env_variable("NUM_KEYS")))
    key_manager = CSEKeyManager(cse_keys)
    
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    df = utils.read_posts(file_name)
    
    total_posts = len(df)
    sucess = 0
    for index, row in df.iterrows():
        link = row[social_network.get_post_url_column()]
        if "instagram" in str(link) or "facebook" in str(link):
            print(f"linha {index + 2} já possui link")
            sucess += 1
            continue
        
        text = row['message']
        text = utils.filter_bmp_characters(text)
        query = social_network.generate_query(text, row['username'])
        post_url = process_search(query, social_network, key_manager)
        
        if post_url:
            df.at[index, social_network.get_post_url_column()] = post_url
            print(f"URL encontrada para a linha {index + 2}: {post_url}")
            sucess += 1
        else:
            print(f"URL não encontrada para a linha {index + 2}")
            # Colocar o link do perfil do usuário
            df.at[index, social_network.get_post_url_column()] = df.at[index, 'profileUrl']
        
    df.to_csv(f'{file_name[:-4]}_com_url.csv', index=False)
                
    json_df = utils.format_data(df, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_df, f'{file_name[:-4]}.json')
    print(f"Posts com links encontrados: {sucess}/{total_posts}")
    
    
if __name__ == '__main__':
    main()