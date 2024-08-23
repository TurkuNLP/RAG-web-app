import json
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate

DATA_PATH = None
DATABASE_ROOT_PATH = None
EMBEDDING_MODEL = None
LLM_MODEL = None
PROMPT_TEMPLATE = None
REPHRASING_PROMPT = None
STANDALONE_PROMPT = None
ROUTER_DECISION_PROMPT = None

def load_api_keys():
    """
    Load API keys from the .env file and set them as environment variables.
    """    
    load_dotenv()
    os.environ["HF_API_TOKEN"] = os.getenv("HF_API_TOKEN")
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
    #os.environ["VOYAGE_API_KEY"] = os.getenv("VOYAGE_API_KEY")


def load_config(config_name = 'default', show_config = False):
    """
    Load configuration settings from a JSON file based on the provided configuration name.
    This function sets global variables for various configuration parameters.

    JSON Structure:
    {
      "config_name": {
        "data_path": "",        # Path to the data folder
        "database_root_path": "", # Path to the folder where the database will be stored
        "embedding_model": "",  # Model to use for embeddings (e.g., 'sentence-transformers/all-mpnet-base-v2', 'openai', 'voyage-law-2')
        "llm_model": "",        # Model to use for the language model (e.g., 'gpt-3.5-turbo', 'mistralai/Mistral-7B-Instruct-v0.1', 'nvidia/Llama3-ChatQA-1.5-8B')
      }
    }
    
    Ready to use models are here. For other model you will maybe need to modify code
    
    Embeddings models : - "sentence-transformers/all-mpnet-base-v2"
                        - "openai"
                        - "voyage-law-2"
                        - "voyage-multilingual-2"
    LLM models :    - "gpt-3.5-turbo"
                    - "mistralai/Mistral-7B-Instruct-v0.1"
                    - "mistralai/Mixtral-8x7B-Instruct-v0.1"
                    - "nvidia/Llama3-ChatQA-1.5-8B"                        
    """
    global DATA_PATH, DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError:
        try:
          with open('python_script/config.json', 'r') as file:
              config = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError("The configuration file cannot be found in the specified paths.")
    except json.JSONDecodeError:
        raise ValueError("The configuration file is present but contains a JSON format error.")
    selected_config = config[config_name]

    DATA_PATH = selected_config['data_path']
    DATABASE_ROOT_PATH = selected_config['database_root_path']
    EMBEDDING_MODEL = selected_config['embedding_model']
    LLM_MODEL = selected_config['llm_model']

    load_prompt(config_name)
    load_api_keys()

    if show_config:
        print_config()

def print_config():
    """
    Print the current configuration settings.
    This function prints the values of the global configuration parameters.
    """
    global DATA_PATH, DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL

    print("\nCurrent Configuration Settings:\n")
    print(f"Data Path: {DATA_PATH}")
    print(f"Database Root Path: {DATABASE_ROOT_PATH}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Language Model: {LLM_MODEL}\n")



def load_prompt(config_name):
    """
    Load the different prompts used in the conversational rag chain
    """
    global PROMPT_TEMPLATE, REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT    
    if config_name == 'arch_ru':
        STANDALONE_PROMPT = PromptTemplate.from_template("""# Context #
        This is part of a conversational retrieval-augmented generator (RAG) AI system to answer user questions. 

        #########

        # Objective #
        Take the original user question and chat history, and generate a new standalone question in russian that can be understood and answered without relying on additional external information.

        #########

        # Style #
        The reshaped standalone question should be clear, concise, and self-contained, while maintaining the intent and meaning of the original query.

        #########

        # Tone #
        Neutral and focused on accurately capturing the essence of the original question.

        #########

        # Audience #
        The audience is the internal system components that will act on the decision.

        #########

        # Response #
        If the original question requires reshaping, provide a new reshaped standalone question in russian that includes all necessary context and information to be self-contained.
        If no reshaping is required, simply output the original question as is in russian.

        ##################

        # Chat History #
        {chat_history}

        #########

        # User original question #
        {question}

        #########

        # The new Standalone question in russian#<|endofprompt|>""")

        PROMPT_TEMPLATE = PromptTemplate.from_template("""# Context #
        This is part of a conversational retrieval-augmented generator (RAG) AI system to answer user questions about russian documents. 

        #########

        # Objective #
        Generate an appropriate response in English to the user's question based only on the retieved context in Russian and the chat history in English.

        #########

        # Style #
        The response should be as detailed as the context allows and follow the order of the conversation.

        #########

        # Tone #
        Analytical and objective.

        #########

        # Audience #
        The audience is the user that ask the question.

        #########

        # Response #
        Provide a detailled awnser in English that is relevant to the context given.

        ##################

        # User question #
        {question}

        #########

        # Chat history #
        {chat_history}

        #########

        # Context retrieved #
        {context}

        #########

        # Your Awnser in English Here #<|endofprompt|>""")
    else:
        PPROMPT_TEMPLATE = PromptTemplate.from_template("""# Context #
        This is part of a conversational retrieval-augmented generator (RAG) AI system to answer user questions. 

        #########

        # Objective #
        Generate an appropriate response to the user's question based only on the retieved context and the chat history.

        #########

        # Style #
        The response should be as detailed as the context allows and follow the order of the conversation.

        #########

        # Tone #
        Analytical and objective.

        #########

        # Audience #
        The audience is the user that ask the question.

        #########

        # Response #
        Provide a detailled awnser that is relevant to the context given.

        ##################

        # User question #
        {question}

        #########

        # Chat history #
        {chat_history}

        #########

        # Context retrieved #
        {context}

        #########

        # Your Awnser Here #<|endofprompt|>""")
        
        STANDALONE_PROMPT = PromptTemplate.from_template("""# Context #
        This is part of a conversational retrieval-augmented generator (RAG) AI system to answer user questions. 

        #########

        # Objective #
        Take the original user question and chat history, and generate a new standalone question that can be understood and answered without relying on additional external information.

        #########

        # Style #
        The reshaped standalone question should be clear, concise, and self-contained, while maintaining the intent and meaning of the original query.

        #########

        # Tone #
        Neutral and focused on accurately capturing the essence of the original question.

        #########

        # Audience #
        The audience is the internal system components that will act on the decision.

        #########

        # Response #
        If the original question requires reshaping, provide a new reshaped standalone question that includes all necessary context and information to be self-contained.
        If no reshaping is required, simply output the original question as is.

        ##################

        # Chat History #
        {chat_history}

        #########

        # User original question #
        {question}

        #########

        # The new Standalone question #<|endofprompt|>""")


    ROUTER_DECISION_PROMPT = PromptTemplate.from_template("""# Context #
    This is part of a conversational AI system that determines whether to use a retrieval-augmented generator (RAG) or a chat model to answer user questions. 

    #########

    # Objective #
    Evaluate the given question and decide whether the RAG application is required to provide a comprehensive answer by retrieving relevant information from a knowledge base, or if the chat model's inherent knowledge is sufficient to generate an appropriate response.

    #########

    # Style #
    The response should be a clear and direct decision, stated concisely.

    #########

    # Tone #
    Analytical and objective.

    #########

    # Audience #
    The audience is the internal system components that will act on the decision.

    #########

    # Response #
    If the question should be rephrased return response in YAML file format:
    ```
        result: true
    ```
    otherwise return in YAML file format:
    ```
        result: false
    ```

    ##################

    # Chat History #
    {chat_history}

    #########

    # User question #
    {question}

    #########

    # Your Decision in YAML format #<|endofprompt|>""")

    REPHRASING_PROMPT = PromptTemplate.from_template("""# Context #
    This is part of a conversational retrieval-augmented generator (RAG) AI system to answer user questions. 

    #########

    # Objective #
    Evaluate the given user question and determine if it requires reshaping according to chat history to provide necessary context and information for answering, or if it can be processed as is.
    Rephrasing is required if the user's question is ambiguous without the context of the previous conversation, or if specific information from the chat history is essential to understand or correctly answer the question.
    #########

    # Style #
    The response should be clear, concise, and in the form of a straightforward decision - either "Reshape required" or "No reshaping required".

    #########

    # Tone #
    Professional and analytical.

    #########

    # Audience #
    The audience is the internal system components that will act on the decision.

    #########

    # Response #
    If the question should be rephrased return response in YAML file format:
    ```
        result: true
    ```
    otherwise return in YAML file format:
    ```
        result: false
    ```

    ##################

    # Chat History #
    {chat_history}

    #########

    # User question #
    {question}

    #########

    # Your Decision in YAML format #<|endofprompt|>""")