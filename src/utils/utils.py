"""Funções úteis"""

import sys
import os
import pandas as pd
import re

MIX_CARACTERES = 100

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