"""This module is responsible for searching the web for relevant URLs."""

import requests
from social_network.social_network import SocialNetwork
from utils import utils
from dotenv import load_dotenv
from googlesearch import search
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


CSE_ID = None
cse_keys: list[list[str, int, bool]] # [key, num_requests, is_active]
gs_active = True

def search_with_cse(query: str, social_network: SocialNetwork, keys: list) -> str:
    """Searches Google for the query and returns the first relevant URL."""

    for k in range(len(keys)):
        if not keys[k][2] or keys[k][1] > 100:  # Se chave estiver desativada or ter atingido 100 requisições, pule para a próxima
            continue
        
        service = build("customsearch", "v1", developerKey=keys[k][0])
        keys[k][1] += 1
        
        try:
            response = service.cse().list(
                q=query,
                cx=CSE_ID,
            ).execute()
            
            if 'items' in response:
                for item in response['items']:
                    link = item['link']
                    if social_network.is_valid_link(link):
                        return link
            return ''
        except HttpError as e:
            if e.resp.status == 429:
                # Acabou a cota da api
                keys[k][2] = False
            else:
                print(f"Erro na requisição: {e}")
                return ''
        

def search_with_gs(query: str, social_network: SocialNetwork) -> str:
    """Searches Google for the query and returns the first relevant URL."""
    try:
        results = search(query, num_results=5, lang='pt-br', sleep_interval=5)
        
        for link in results:
            if social_network.is_valid_link(link):
                return link
        return ''
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Acabou a cota da api")
            global gs_active
            gs_active = False
            return ''
        else:
            print(f"Erro na requisição: {e}")
            return ''
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return ''


def main():
    global CSE_ID
    CSE_ID = utils.env_variable("CSE_ID")
    cse_keys = utils.get_cse_keys()
    
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    data_posts = utils.read_posts(file_name)
    posts_without_url = data_posts # Copiar o DataFrame para manter os posts sem URL
    
    # Converter a coluna de URLs para string
    url_column = social_network.get_post_url_column()
    data_posts[url_column] = data_posts[url_column].astype(str)
    
    global gs_active
    for index, row in data_posts.iterrows():
        text = row['message']
        text = utils.filter_bmp_characters(text)
        
        query = social_network.generate_query(text, row['username'])
        cse_post_url = search_with_cse(query, social_network, cse_keys)
        
        if cse_post_url:
            cse_post_url = utils.extract_relevant_url(cse_post_url)
            data_posts.at[index, social_network.get_post_url_column()] = cse_post_url
            print(f"URL encontrada pelo cse para a linha {index + 2}: {cse_post_url}")
            posts_without_url.drop(index, inplace=True)  # Remover a linha
        else:
            # Tentar pelo outro método
            gs_post_url = search_with_gs(query, social_network) if gs_active else ''
            if gs_post_url:
                gs_post_url = utils.extract_relevant_url(gs_post_url)
                data_posts.at[index, social_network.get_post_url_column()] = gs_post_url
                print(f"URL encontrada pelo gs para a linha {index + 2}: {gs_post_url}")
                posts_without_url.drop(index, inplace=True)  # Remover a linha
            else:
                print(f"URL não encontrada para a linha {index + 2}")
                data_posts.drop(index, inplace=True)  # Remover a linha
                
    json_data_posts = utils.format_data(data_posts, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_data_posts, f'{file_name[:-4]}.json')
    posts_without_url.to_csv(f'{file_name[:-4]}_sem_url.csv', index=False)
    
if __name__ == '__main__':
    load_dotenv()
    main()