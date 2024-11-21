"""Formatter module"""

from social_network.social_network import SocialNetwork
from utils import utils
import csv


def main():
    social_network = SocialNetwork.get_social_network()
    file_name = utils.list_files_and_get_input()
    utils.validate_file_extension(file_name, '.csv')
    
    df = utils.read_posts(file_name)
    
    df = utils.clean_df(df)
    df = social_network.fix_df(df)

    df.to_csv(
        path_or_buf=file_name,
        index=False,
        quotechar='"',
        quoting=csv.QUOTE_ALL
    )

    print("Arquivo formatado com sucesso")


if __name__ == '__main__':
    main()
    