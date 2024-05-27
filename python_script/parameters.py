import json
import os
from dotenv import load_dotenv

def load_api_keys():
    """
    Load API keys from the .env file and set them as environment variables.
    """    
    load_dotenv()
    os.environ["HF_API_TOKEN"] = os.getenv("HF_API_TOKEN")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    os.environ["VOYAGE_API_KEY"] = os.getenv("VOYAGE_API_KEY")

def load_config(config_name):
    """
    Load configuration settings from a JSON file based on the provided configuration name.
    This function sets global variables for various configuration parameters.

    JSON Structure:
    {
      "config_name": {
        "data_path": "",        # Path to the data folder
        "chroma_root_path": "", # Path to the folder where the Chroma database will be stored
        "embedding_model": "",  # Model to use for embeddings (e.g., 'sentence-transformers/all-mpnet-base-v2', 'openai', 'voyage-law-2')
        "llm_model": "",        # Model to use for the language model (e.g., 'gpt-3.5-turbo', 'mistralai/Mistral-7B-Instruct-v0.1', 'nvidia/Llama3-ChatQA-1.5-8B')
        "prompt_template": ""   # Template for the prompt
      }
    }
    
    Ready to use models are here. For other model you will maybe need to modify code
    Embeddings models : - "sentence-transformers/all-mpnet-base-v2"
                        - "openai"
                        - "voyage-law-2"
    LLM models :    - "gpt-3.5-turbo"
                    - "mistralai/Mistral-7B-Instruct-v0.1"
                    - "mistralai/Mixtral-8x7B-Instruct-v0.1"
                    - "nvidia/Llama3-ChatQA-1.5-8B"                        
    """    
    global DATA_PATH, CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE
    with open('config.json', 'r') as file:
        config = json.load(file)
    selected_config = config[config_name]
    DATA_PATH = selected_config['data_path']
    CHROMA_ROOT_PATH = selected_config['chroma_root_path']
    EMBEDDING_MODEL = selected_config['embedding_model']
    LLM_MODEL = selected_config['llm_model']
    PROMPT_TEMPLATE = selected_config['prompt_template']