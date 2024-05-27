def get_embedding_function(model = "voyage"):
    if model == "sentence-transformers/all-mpnet-base-v2":
        from langchain.embeddings.huggingface import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        
    elif model == "openai":
        from langchain_community.embeddings import OpenAIEmbeddings
        embeddings = OpenAIEmbeddings()
        
    elif model == "voyage-law-2":
        from langchain_voyageai import VoyageAIEmbeddings
        embeddings = VoyageAIEmbeddings(model="voyage-law-2")
        
    else:
        # TODO create error message
        print("You have to chose a model")
        return
    return embeddings
