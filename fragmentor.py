"""Pega um arquivo csv e divide ele em arquivos menores."""

import os
import sys
import pandas as pd

MAX_LINES = 500

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


def read_posts_from_extraction(file_path: str) -> pd.DataFrame:
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


def map_columns(choice: int):
    #TODO pegar o tema

    if choice == 1: # Instagram
        #Content Librarry, export comments, value
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
    elif choice == 2: #Facebook
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
        print("Opção inválida")
        sys.exit(1)


def main():
    file_name = list_files_and_get_input()
    validate_file_extension(file_name, '.csv')
    data_posts = read_posts_from_extraction(file_name)
    
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