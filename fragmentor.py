"""Pega um arquivo csv e divide ele em arquivos menores."""

from enum import Enum
import utils


MAX_LINES = 500

class SocialNetwork(Enum):
    """Social networks collected by Content Library"""
    INSTAGRAM = 'https://www.instagram.com/'
    FACEBOOK = 'https://www.facebook.com/'
    
    def remaped_columns(self) -> list:
        """Return a list of tuples with the original column name, the new column name and the default value."""
        if self == self.__class__.INSTAGRAM:
            return [
                ('post_owner.name','name', ''),
                ('creation_time', 'time', ''),
                ('statistics.like_count', 'likes', ''),
                ('text', 'message', ''),
                ('post_owner.id', 'profileId', ''),
                ('', 'commentId', None), #Null in export comments
                ('post_owner.username', 'username', ''),
                ('', 'parentCommentId', None), #Null in export comments
                ('', 'replies', None), #Null in export comments
                ('', 'reply', False), #False
                ('', 'shortcode', ''), #obter quando conseguir o link
                ('', 'reaction', None), # Null in export comments
                ('media_type', 'isVideo'), #verificar o media_type #TODO
                ('statistics.comment_count', 'comments', ''),
                ('', 'url'), #obter
                ('', 'profileUrl'), #obter a partir do username #TODO
                ('statistics.views', 'videoViewCount', ''),
                ('', 'isPrivateUser', None), # Null in export comments
                ('', 'isVerifiedUser', None), # Null in export comments
                ('', 'displayUrl', ''),
                ('', 'followersCount', ''), # Sempre zero
                ('id', 'id', ''),
                ('', 'caption', None), # Null in export commments
                ('', 'thumbnail', None), # Null in export commments
                ('', 'accessibilityCaption', None), # Null in export commments
                ('', 'commentsDisabled', None), # Not found in content library (null)
                ('', 'videoDuration', ''),
                ('media_type', 'productType', ''),
                ('', 'isSponsored', False), # Sempre falso
                ('', 'locationName', None), # Null in export commments
                ('', 'mediaCount', None), # Null in export commments
                ('multimedia', 'media', '')
                ('', 'owner', None) #Null in export commments
                ('', 'profileImage', None), # not found (null)
                ('hashtags', 'terms', ''),    
            ]
        elif self == self.__class__.FACEBOOK:
            return [
                ('id', 'id', ''),
                ('post_owner.name','name', ''),
                ('post_owner.username', 'nickName', ''),
                ('creation_time', 'time', ''),
                ('text', 'message', ''),
                ('post_owner.id', 'profileId', ''),
                ('', 'postId', '') # Não tem
                ('multimedia', 'media', '')
                ('', 'attachments', None) # Null in export comments
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
                ('', 'profileUrl', 'profileUrl') #TODO pegar a partir do nome
                ('', 'postUrl', '') #TODO pega
                ('', 'adUrl', '') # Not found in Content library
            ]
        else:
            raise ValueError(f"Rede social inválida {self}.")
            
            
def main():
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    data_posts = utils.read_posts(file_name)
    
    prev_length = len(data_posts)
    data_posts = data_posts.drop_duplicates(subset='id')
    duplicates = prev_length - len(data_posts)

    part = 1
    for i in range(0, len(data_posts), MAX_LINES):
        data_posts[i:i+MAX_LINES].to_csv(f'{file_name}_part{part}.csv', index=False),
        part += 1
    print(f"Arquivo dividido em {part-1} partes.")
    
    
if __name__ == '__main__':
    main()