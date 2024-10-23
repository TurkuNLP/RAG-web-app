def get_embedding_function(model_name = "voyage"):
    """get Embedding model between :
    - sentence-transformers/all-mpnet-base-v2
    - openai
    - voyage-2
    - voyage-law-2
    - voyage-multilingual-2
    - Other models can of course be implemented later"""
    if model_name == "sentence-transformers/all-mpnet-base-v2":
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        
    elif model_name == "openai":
        from langchain_community.embeddings import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
        
    elif model_name == "voyage-2":
        from langchain_voyageai import VoyageAIEmbeddings
        embeddings = VoyageAIEmbeddings(model="voyage-2")

    elif model_name == "voyage-law-2":
        from langchain_voyageai import VoyageAIEmbeddings
        embeddings = VoyageAIEmbeddings(model="voyage-law-2")

    elif model_name == "voyage-multilingual-2":
        #print("/!\ WARNING /!\ \n")
        #print("Out of free token for this model chose another one")
        from langchain_voyageai import VoyageAIEmbeddings
        embeddings = VoyageAIEmbeddings(model="voyage-multilingual-2")        
        
    else:
        print(f'Model "{model_name}" is not implemented on the system.')
        return
    return embeddings
