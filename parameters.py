import os
from dotenv import load_dotenv
# Define path to datas folder and the chroma folder where the associated database will be stored
# Note that DATA_PATH will be used only if you actualise the database
DATA_PATH = "ship_data"
CHROMA_ROOT_PATH = "ship_chroma"

# Enter your api keys here
load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

os.environ["VOYAGE_API_KEY"] = VOYAGE_API_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Define the models you will use here
"""
Ready to use models are here. For other model you will maybe need to modify code
Embeddings models : - "sentence-transformers/all-mpnet-base-v2"
                    - "openai"
                    - "voyage-law-2"
"""
EMBEDDING_MODEL = "voyage-law-2"
"""
Ready to use models are here. For other model you will maybe need to modify code
LLM models :    - "gpt-3.5-turbo"
                - "mistralai/Mistral-7B-Instruct-v0.1"
                - "mistralai/Mixtral-8x7B-Instruct-v0.1"
                - "nvidia/Llama3-ChatQA-1.5-8B"
"""
LLM_MODEL = "gpt-3.5-turbo"

# Define prompt template here
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""