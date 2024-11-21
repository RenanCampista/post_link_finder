"""Module to handle the social networks collected by Content Library. """

import pandas as pd
from enum import Enum
from difflib import SequenceMatcher


class SocialNetwork(Enum):
    """Social networks collected by Content Library"""
    FACEBOOK = 'facebook'
    INSTAGRAM = 'instagram'
    
    @property
    def url(self):
        return f'https://www.{self.value}.com/'
        
    @staticmethod 
    def get_social_network() -> 'SocialNetwork':
        print('Escolha a rede social:\n1 - Instagram\n2 - Facebook')
        option = input()
        if option == '1':
            return SocialNetwork.INSTAGRAM
        elif option == '2':
            return SocialNetwork.FACEBOOK
        else:
            print('Opção inválida.')
            return SocialNetwork.get_social_network()
    
    def is_valid_link(self, link: str, title: str, post_text: str) -> bool:
        """Checks if the link is valid for the post."""
        # Comparar a mesma quantidade de caracteres
        similarity_ratio = SequenceMatcher(None, title, post_text[:len(title)]).ratio()
        return similarity_ratio >= 0.45 and self.url in link
    
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
            raise ValueError(f'Rede social inválida {self}.')
        
    def generate_profile_url(self, username: str) -> str:
        """Generate the profile URL based on the username."""
        return f'{self.url}{username}'    
             
    def generate_query(self, post_text: str, username: str) ->str:
        """Generates the query for the search."""
        return f'{self.value} {username}: {post_text}'
          
    def fix_df(self, posts_cl: pd.DataFrame) -> pd.DataFrame:
        """Fix the DataFrame based on the social network."""
        df_fixed = pd.DataFrame()
        
        for cl_column, ec_column, value in self.mapping_columns():
            if cl_column in posts_cl.columns:
                df_fixed[ec_column] = posts_cl[cl_column]
            else:
                df_fixed[ec_column] = value

        # Verificar se a coluna 'username' existe
        if 'username' not in df_fixed.columns:
            df_fixed['username'] = None  # Adicionar coluna 'username' com valores padrão

        if df_fixed['username'].notnull().any():
            df_fixed['profileUrl'] = df_fixed['username'].apply(self.generate_profile_url())

        return df_fixed