"""Fragmentor module"""

from social_network.social_network import SocialNetwork
from utils import utils
import csv

MAX_LINES = 500

def main():
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    
    df = utils.read_posts(file_name)
    df_filtred = utils.clean_df(df)
    df_fixed = social_network.fix_df(df_filtred)

    part = 1
    for i in range(0, len(df_fixed), MAX_LINES):
        part_df = df_fixed[i:i+MAX_LINES]
        part_df.to_csv(
            path_or_buf=f"{file_name[:-4]}_part{part}.csv", 
            index=False, 
            quotechar='"', 
            quoting=csv.QUOTE_ALL
        )
        part += 1
    print(f"Arquivo {file_name} foi dividido em {part-1} partes.")


if __name__ == '__main__':
    main()