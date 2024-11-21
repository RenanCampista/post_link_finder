from googlesearch import search, SearchResult
import requests
from social_network.social_network import SocialNetwork


class SearchManager:
    def __init__(self):
        self.quota_exceeded = False
        self.success_search = 0
        
    def get_success_searches(self) -> int:
        """Returns the number of successful searches."""
        return self.success_search
        
    def search_post(self, post_text: str, username: str, social_network: SocialNetwork) -> str:
        """Processes the search for the post URL."""
        query = social_network.generate_query(post_text, username)
        try:
            SearchResult = search(
                term=query,
                lang='pt-br',
                timeout=20,
                safe=None,
                advanced=True
            )

            for result in SearchResult:
                if social_network.is_valid_link(
                    link=str(result.url),
                    title=str(result.title),
                    post_text=post_text
                ):
                    self.success_search += 1
                    return result.url
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print('Atigiu limite de requisições')
                self.quota_exceeded = True
            else:
                print(f'Erro na requisição: \n{e}')
        except Exception as e:
            print(f'Erro na requisição: \n{e}')
        
        return ''