"""Pega um arquivo csv e divide ele em arquivos menores."""

from utils.utils import SocialNetwork
import utils.utils as utils
import pandas as pd

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
        data_posts_fixed[i:i+MAX_LINES].to_csv(f'{file_name[:-4]}_part{part}.csv', index=False),
        part += 1
    print(f"Arquivo {file_name} foi dividido em {part-1} partes.")

    
if __name__ == '__main__':
    main()