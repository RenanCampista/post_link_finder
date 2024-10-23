"""Utility functions for the Content Library project."""

from enum import Enum
import sys
import os
import pandas as pd
import re
from urllib.parse import urlparse
import json

MIX_CARACTERES = 150


def env_variable(var_name: str) -> str:
    """Gets an environment variable or raises an exception if it is not set."""    
    if not (var_value := os.getenv(var_name)):
        raise ValueError(f"Variável de ambiente {var_name} não definida. Verifique o arquivo .env.")
    return var_value


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
  
  
def filter_bmp_characters(text: str) -> str:
    """Remove characters outside the Basic Multilingual Plane (BMP)."""
    return re.sub(r'[^\u0000-\uFFFF]', '', text)


def get_cse_keys(num_keys: int) -> list:
    """Get the API keys for the Custom Search Engine."""
    cse_keys: list # # [key, num_requests, is_active]]
    
    cse_keys = [
        env_variable(f"CSE_API_KEY_{i}") for i in range(num_keys)
    ]
    
    return cse_keys
         
                
def read_posts(file_path: str) -> pd.DataFrame:
    """Reads the CSV file with the posts and returns a DataFrame."""
    validate_file_extension(file_path, '.csv')
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
    data_posts = data_posts.drop_duplicates(subset='text')
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


def extract_relevant_url(url: str) -> str:
    """Extracts the relevant part of the URL."""
    if not url: return ''
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


def extract_theme_from_filename(filename: str) -> str:
    """Extracts the theme from the filename, considering composite names."""
    # Regex to match the date pattern in the filename
    match = re.search(r'_\d{2}_\d{2}_\d{2}_', filename)
    if match:
        theme = filename[:match.start()]
    else:
        theme = filename.split('_')[0]  # Fallback if no date pattern is found
    return theme.lower()
    

def format_data(data_posts: pd.DataFrame, theme: str) -> list:
    data_posts = data_posts.fillna('')
    data_posts = data_posts.replace("Null", None)
    formatted_data = []
    for _, row in data_posts.iterrows():
        formatted_data.append({
            "body": row.to_dict(),
            "metadata": {
                "theme": theme,
                "terms": '',
                "api_version": 'ContentLibrary'
            }
        })
    return formatted_data


def save_to_json(data: list, filename: str):
    """Saves a list of data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)