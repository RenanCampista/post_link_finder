"""Pega um arquivo csv e divide ele em arquivos menores."""

from enum import Enum
import utils.utils as utils
import pandas as pd

MAX_LINES = 500

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
             
    def fix_df(self, posts_cl: pd.DataFrame) -> pd.DataFrame:
        """Fix the DataFrame based on the social network."""
        df_fixed = pd.DataFrame()
        
        for cl_column, ec_column, value in self.mapping_columns():
            df_fixed[ec_column] = posts_cl[cl_column] if cl_column else value

        df_fixed['profileUrl'] = df_fixed['username'].apply(self.generate_profile_url)

        return df_fixed
            
            
def main():
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    
    data_posts = utils.read_posts(file_name)
    data_posts_filtred = utils.clean_data_posts(data_posts)
    data_posts_fixed = social_network.fix_df(data_posts_filtred)

    part = 1
    for i in range(0, len(data_posts_fixed), MAX_LINES):
        data_posts_fixed[i:i+MAX_LINES].to_csv(f'{file_name[:-4]}_part{part}.csv', index=False),
        part += 1
    print(f"Arquivo {file_name} foi dividido em {part-1} partes.")

    
if __name__ == '__main__':
    main()