"""Fragmentor module"""

from social_network.social_network import SocialNetwork
from utils import utils

MAX_LINES = 500

def main():
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    
    data_posts = utils.read_posts(file_name)
    data_posts_filtred = utils.clean_data_posts(data_posts)
    data_posts_fixed = social_network.fix_df(data_posts_filtred)

    part = 1
    for i in range(0, len(data_posts_fixed), MAX_LINES):
        part_df = data_posts_fixed[i:i+MAX_LINES]
        part_string = part_df.to_string(index=False)
        with open(f'{file_name[:-4]}_part{part}.txt', 'w', encoding='utf-8') as file:
            file.write(part_string)
        part += 1
    print(f"Arquivo {file_name} foi dividido em {part-1} partes.")

if __name__ == '__main__':
    main()