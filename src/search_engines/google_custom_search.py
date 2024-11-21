from social_network.social_network import SocialNetwork
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CSEKey:
    def __init__(self, key: str):
        self.key = key
        self.num_requests = 0
        self.is_active = True

    def increment_requests(self):
        self.num_requests += 1
        if self.num_requests > 100:
            print(f'\033[91mChave{self.key} atingiu o limite diário de requisições. Chave desativada.\033[0m')
            self.is_active = False
            
            
class CSEManager:
    def __init__(self, keys: list[str], cse_id: str):
        self.keys = [CSEKey(key) for key in keys]
        self.success_searches = 0
        self.all_keys_off = False
        self.cse_id = cse_id

    def get_active_key(self):
        for key in self.keys:
            if key.is_active:
                return key
        return None
    
    def get_success_searches(self):
        return self.success_searches

    def search_post(self, post_text: str, username:str, social_network: SocialNetwork) -> str:
        """Searches Google for the query and returns the first relevant URL."""
        while True:
            key = self.get_active_key()
            if not key:
                if not self.all_keys_off:
                    print('\033[91mTodas as chaves CSE atingiram o limite de requisições. Desativando CSE.\033[0m')
                    self.all_keys_off = True
                return ''
            
            service = build('customsearch', 'v1', developerKey=key.key)
            key.increment_requests()
            query = social_network.generate_query(post_text, username) 
            
            try:
                response = service.cse().list(
                    q=query, 
                    cx=self.cse_id,
                    safe='off',
                    hl='pt-BR'
                ).execute()
                if 'items' in response:
                    for item in response['items']:
                        link = item['link']
                        title = item['title']
                        
                        if social_network.is_valid_link(
                            link=link, 
                            title=title, 
                            post_text=post_text
                        ):
                            self.success_searches += 1
                            return link
            except HttpError as e:
                if e.resp.status == 429:
                    print(f'\033[91mKey {key.key} atingiu o limite de requisições. Desativando chave...\033[0m')
                    key.is_active = False
                else:
                    print(f"Request error: {e}")
                    return '' 
            return ''