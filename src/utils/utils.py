"""Funções úteis"""

from enum import Enum
import sys
import os
import pandas as pd
import re
from urllib.parse import urlparse

MIX_CARACTERES = 100


class SocialNetwork(Enum):
    """Social networks collected by Content Library"""
    INSTAGRAM = 'https://www.instagram.com/'
    FACEBOOK = 'https://www.facebook.com/'
    
    
    def __init__(self, url):
        self.url = url
        
    @staticmethod 
    def get_social_network() -> 'SocialNetwork':
        print("Escolha a rede social:\n1 - Instagram\n2 - Facebook")
        option = input()
        if option == '1':
            return SocialNetwork.INSTAGRAM
        elif option == '2':
            return SocialNetwork.FACEBOOK
        else:
            print("Opção inválida.")
            return SocialNetwork.get_social_network()
        
    def get_post_url_column(self) -> str:
        if self == self.__class__.INSTAGRAM:
            return 'url'
        elif self == self.__class__.FACEBOOK:
            return 'postUrl'
        else:
            raise ValueError(f"Rede social inválida {self}.")
    
    def is_valid_link(self, link: str) ->bool:
        if self == self.__class__.INSTAGRAM:
            if self.url in link and any(substring in link for substring in ["p/", "tv/", "reel/", "video/", "photo/"]):
                return True
            return False
        elif self == self.__class__.FACEBOOK:
            if self.url in link and any(substring in link for substring in ["posts/", "videos/", "photos/", "groups/"]):
                return True
            return False
        else:
            raise ValueError(f"Rede social inválida {self}.")
    
    def mapping_columns(self) -> list:
        """Return a list of tuples with the original column name, the new column name and the default value."""
        if self == self.__class__.INSTAGRAM:
            return [
                ('post_owner.name','name', ''),
                ('creation_time', 'time', ''),
                ('statistics.like_count', 'likes', ''),
                ('text', 'message', ''),
                ('post_owner.id', 'profileId', ''),
                ('', 'commentId', None), 
                ('post_owner.username', 'username', ''),
                ('', 'parentCommentId', None), 
                ('', 'replies', None),
                ('', 'reply', False),
                ('', 'shortcode', ''),
                ('', 'reaction', None),
                ('', 'isVideo', ''), #TODO: verificar o media_type 
                ('statistics.comment_count', 'comments', ''),
                ('', 'url', ''),
                ('', 'profileUrl', ''),
                ('statistics.views', 'videoViewCount', ''),
                ('', 'isPrivateUser', None),
                ('', 'isVerifiedUser', None),
                ('', 'displayUrl', ''),
                ('', 'followersCount', ''),
                ('id', 'id', ''),
                ('', 'caption', None),
                ('', 'thumbnail', None),
                ('', 'accessibilityCaption', None),
                ('', 'commentsDisabled', None),
                ('', 'videoDuration', ''),
                ('media_type', 'productType', ''),
                ('', 'isSponsored', False), 
                ('', 'locationName', None),
                ('', 'mediaCount', None),
                ('multimedia', 'media', ''),
                ('', 'owner', None),
                ('', 'profileImage', None),
                ('hashtags', 'terms', '')    
            ]
        elif self == self.__class__.FACEBOOK:
            return [
                ('id', 'id', ''),
                ('post_owner.name','name', ''),
                ('post_owner.username', 'nickName', ''),
                ('creation_time', 'time', ''),
                ('text', 'message', ''),
                ('post_owner.id', 'profileId', ''),
                ('', 'postId', ''),
                ('multimedia', 'media', ''),
                ('', 'attachments', None),
                #('', 'countReactionTypes', '') # Não terá esse. Reações separadas abaixo
                ('statistics.comment_count', 'countComment', ''),
                ('statistics.views', 'countSeen', ''),
                ('statistics.share_count', 'countShare', ''),
                ('statistics.reaction_count', 'countReaction', ''),
                ('statistics.like_count', 'countLike', ''),
                ('statistics.love_count', 'countLove', ''),
                ('statistics.care_count', 'countCare', ''),
                ('statistics.haha_count', 'countHaha', ''),
                ('statistics.wow_count', 'countWow', ''),
                ('statistics.sad_count', 'countSad', ''),
                ('statistics.angry_count', 'countAngry', ''),
                ('', 'profileUrl', ''),
                ('', 'postUrl', ''),
                ('', 'adUrl', '')
            ]
        else:
            raise ValueError(f"Rede social inválida {self}.")
        
    def generate_profile_url(self, username: str) -> str:
        """Generate the profile URL based on the username."""
        return f"{self.url}{username}"
             
    def generate_alternative_query(self, query: str) ->str:
        if self == self.__class__.INSTAGRAM:
            return f'site:+instagram.com+{query}'
        elif self == self.__class__.FACEBOOK:
            return f'site:+facebook.com+{query}'
        else:
            raise ValueError(f"Rede social inválida {self}.")
             
    def fix_df(self, posts_cl: pd.DataFrame) -> pd.DataFrame:
        """Fix the DataFrame based on the social network."""
        df_fixed = pd.DataFrame()
        
        for cl_column, ec_column, value in self.mapping_columns():
            df_fixed[ec_column] = posts_cl[cl_column] if cl_column else value

        df_fixed['profileUrl'] = df_fixed['username'].apply(self.generate_profile_url)

        return df_fixed



def env_variable(var_name: str) -> str:
    """Gets an environment variable or raises an exception if it is not set."""    
    if not (var_value := os.getenv(var_name)):
        raise ValueError(f"Variável de ambiente {var_name} não definida. Verifique o arquivo .env.")
    return var_value


def validate_file_extension(file_name: str, extension: str):
    """Check if the file has the correct extension."""
    if not file_name.endswith(extension):
        print(f"Arquivo inválido. O arquivo deve ser um {extension}")
        sys.exit(1) 
        

def list_files_and_get_input() -> str:
    """List files and get user input for file selection."""
    files = [file for file in os.listdir('.') if os.path.isfile(file) and not file.startswith('.')]
    while True:
        user_input = input('Please enter the file name ("?" to list): ')
        if user_input == '?':
            for i, file in enumerate(files, 1):
                print(f"{i}. {file}")
        elif user_input.isdigit():
            file_index = int(user_input) - 1
            if 0 <= file_index < len(files):
                return files[file_index]
            else:
                print("Invalid number. Please try again.")      
        else:
            if user_input in files:
                return user_input
            else:
                print("Invalid file name. Please try again.")
  
  
def filter_bmp_characters(text: str) -> str:
    """Remove characters outside the Basic Multilingual Plane (BMP)."""
    return re.sub(r'[^\u0000-\uFFFF]', '', text)
              
                
def read_posts(file_path: str) -> pd.DataFrame:
    """Reads the CSV file with the posts and returns a DataFrame."""
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
        sys.exit(1)
    except pd.errors.ParserError:
        print(f"Erro ao ler o arquivo: {file_path}")
        sys.exit(1)
    except KeyError as e:
        print(f"Coluna não encontrada: {e}")
        sys.exit(1)
        

def clean_data_posts(data_posts: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and posts with less than min caracteres characters."""
    prev_length = len(data_posts)
    
    # Remove posts duplicados
    data_posts = data_posts.drop_duplicates(subset='id')
    duplicates = prev_length - len(data_posts)

    # Remove posts com menos de MIX_CARACTERES caracteres
    data_posts = data_posts[data_posts['text'].str.len() >= MIX_CARACTERES]
    min_caracteres_removed = prev_length - len(data_posts)

    # Remove quebras de linha e vírgulas do campo 'text'
    data_posts['text'] = data_posts['text'].apply(lambda x: re.sub(r'[,\r\n]', ' ', str(x)))

    print(f"\nTotal de posts lidos: {prev_length}.")
    print(f"Posts com menos de {MIX_CARACTERES} caracteres: {prev_length - len(data_posts)}.")
    print(f"Posts duplicados: {duplicates}.")
    print(f"Posts restantes: {prev_length - duplicates - min_caracteres_removed}.")
    
    return data_posts


def extract_relevant_url(url: str) -> str:
    """Extracts the relevant part of the URL."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"