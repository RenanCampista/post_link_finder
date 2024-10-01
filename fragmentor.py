"""Pega um arquivo csv e divide ele em arquivos menores."""

import os
import sys
import pandas as pd

MAX_LINES = 300

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


def main():
    file_name = list_files_and_get_input()
    validate_file_extension(file_name, '.csv')
    data_posts = read_posts_from_extraction(file_name)
    
    length = len(data_posts)
    data_posts = data_posts.drop_duplicates(subset='Caption') # It should be post_id, but we don't have that information
    print(f"Foram removidos {length - len(data_posts)} posts duplicados.")

    part = 1
    for i in range(0, len(data_posts), MAX_LINES):
        data_posts[i:i+MAX_LINES].to_csv(f'{file_name}_part{part}.csv', index=False),
        part += 1
    print(f"Arquivo dividido em {part-1} partes.")
    
    
if __name__ == '__main__':
    main()