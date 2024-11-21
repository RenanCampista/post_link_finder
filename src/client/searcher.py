"""This module is responsible for searching the web for relevant URLs."""

from social_network.social_network import SocialNetwork
from search_engines.google_custom_search import CSEManager
from search_engines.google_lib_search import SearchManager
import pandas as pd
from utils import utils
from dotenv import load_dotenv
import sys
import signal


def process_search(post_text: str, username:str, social_network: SocialNetwork, cse: CSEManager, gs: SearchManager) -> tuple:
    """Try searching using all available mechanisms."""
    post_url = cse.search_post(post_text, username, social_network)
    search_engine = 'cse'

    if not post_url:
        post_url = gs.search_post(post_text, username, social_network)
        search_engine = 'gs'
        
    return utils.extract_relevant_url(post_url), search_engine


def main():
    load_dotenv()
    cse_keys = utils.get_cse_keys(int(utils.env_variable('NUM_KEYS')))
    cse_manager = CSEManager(
        keys=cse_keys,
        cse_id=utils.env_variable('CSE_ID')
    )
    
    google_search = SearchManager()
    
    social_network = SocialNetwork.get_social_network()
    
    file_name = utils.list_files_and_get_input()
    df = utils.read_posts(file_name)
    
    signal.signal(signal.SIGINT, lambda sig, frame: utils.signal_handler(sig, frame, df, file_name))
    
    success = 0
    for index, row in df.iterrows():
        if google_search.quota_exceeded:
            print('\033[91mProcessamento paralisado pois as ferramentas de busca tiveram suas cotas esgotadas\033[0m')
            break
        
        try:
            username = row.get('username') or row.get('Username')
            text = row.get('message') or row.get('Caption')
            post_url = row.get('url') or row.get('URL')
        except KeyError as e:
            print(f'Coluna não encontrada: {e}')
            sys.exit(1)
        
        profile_url = social_network.generate_profile_url(username)
        if pd.notna(post_url):
            print(f'linha {index + 2} já possui link')
            if post_url != profile_url:
                success += 1
            continue
        
        text = utils.filter_bmp_characters(text)
        post_url, search_engine = process_search(text, username, social_network, cse_manager, google_search)
        
        if post_url:
            print(f'URL encontrada para a linha {index + 2} pelo {search_engine}: {post_url}')
        else:
            print(f'URL não encontrada para a linha {index + 2}')
        
        df.loc[index, 'url' if 'url' in df.columns else 'URL'] = post_url or profile_url
        
    df.to_csv(f'{file_name[:-4]}.csv', index=False)
                
    json_df = utils.format_data(df, utils.extract_theme_from_filename(file_name))
    utils.save_to_json(json_df, f'{file_name[:-4]}.json')
    print(f"""Posts com links encontrados: {
        success + 
        google_search.get_success_searches() + 
        cse_manager.get_success_searches()}/{len(df)}""")
    
    
if __name__ == '__main__':
    main()