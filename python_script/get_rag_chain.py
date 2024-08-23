from parameters import DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL

from get_embedding_function import get_embedding_function
from get_llm_function import get_llm_function
from populate_database import find_database_path

from langchain.vectorstores.chroma import Chroma
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

import faiss                  
import numpy as np

def get_rag_chain(params = None):
    """
    Creates RAG chain for question-answering tasks using specified models and settings.
     
    configures the retriever to fetch relevant documents based on similarity, similarity with a score threshold,
    orMaximal Marginal Relevance (MMR).
    
    The function also supports context-aware question reformulation if chat history is utilized.

    Parameters:
        params (dict, optional): A dictionary of configuration parameters.
            - chroma_root_path (str): The root path for Chroma data storage.
            - embedding_model (str): The model name for the embedding function.
            - llm_model (str): The model name for the language model.
            - search_type (str): The type of search to perform. Options are:
                - "similarity": Retrieve based on document similarity.
                - "similarity_score_threshold": Retrieve based on similarity with a score threshold.
                - "mmr": Retrieve using Maximal Marginal Relevance.
            - similarity_doc_nb (int): Number of documents to return for similarity search.
            - score_threshold (float): The score threshold for filtering documents in "similarity_score_threshold" mode.
            - max_chunk_return (int): Maximum number of chunks to return.
            - considered_chunk (int): Number of chunks to consider in MMR search.
            - mmr_doc_nb (int): Number of documents to return for MMR search.
            - lambda_mult (float): The trade-off parameter between relevance and diversity in MMR.
            - isHistoryOn (bool): Indicates if history-based question reformulation is enabled.

    Returns:
        A RAG chain object ready for processing question-answering tasks.
    """
    
    default_params = {
        "chroma_root_path": DATABASE_ROOT_PATH,
        "embedding_model": EMBEDDING_MODEL,
        "llm_model": LLM_MODEL,
        "search_type": "similarity",
        "similarity_doc_nb": 5,
        "score_threshold": 0.8,
        "max_chunk_return": 5,
        "considered_chunk": 25,
        "mmr_doc_nb": 5,
        "lambda_mult":0.5,
        "isHistoryOn": True,
    }
    if params is None :
        params = default_params
    else:
        params = {**default_params, **params}

    try:
        required_keys = ["chroma_root_path", "embedding_model", "llm_model"]
        for key in required_keys:
            if key not in params:
                raise NameError(f"Required setting '{key}' not defined.")
        
        embedding_model = get_embedding_function(model_name=params["embedding_model"])
        llm = get_llm_function(model_name=params["llm_model"])
        db = Chroma(persist_directory=find_database_path(model_name=params["embedding_model"], base_path=params["chroma_root_path"]), embedding_function=embedding_model)
        """
        import faiss
        import numpy as np

        # Load the FAISS index from disk
        index = faiss.read_index('faiss_index.bin')

        vector_store = FAISS(
            embedding_function=OpenAIEmbeddings(),
            index=index,
            docstore= InMemoryDocstore(),
            index_to_docstore_id={}
        )
        results = vector_store.similarity_search(query="thud",k=1)


        """
        search_type = params["search_type"]
        if search_type == "similarity":
            retriever = db.as_retriever(search_type=search_type, search_kwargs={"k": params["similarity_doc_nb"]})
        elif search_type == "similarity_score_threshold":
            retriever = db.as_retriever(search_type=search_type, search_kwargs={"k": params["max_chunk_return"],"score_threshold": params["score_threshold"]})
        elif search_type == "mmr":
            retriever = db.as_retriever(search_type=search_type, search_kwargs={"k": params["mmr_doc_nb"], "fetch_k": params["considered_chunk"], "lambda_mult": params["lambda_mult"]})
        else:
            raise ValueError("Invalid 'search_type' setting")
        
    except NameError as e:
        variable_name = str(e).split("'")[1]
        raise NameError(f"{variable_name} isn't defined")
         
    if params["isHistoryOn"]:
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ]
        )

        history_aware_retriever = create_history_aware_retriever(
            llm, retriever, contextualize_q_prompt
        )
        retriever = history_aware_retriever

    qa_system_prompt = """You are an assistant for question-answering tasks. \
    Use the following pieces of retrieved context to answer the question. \
    If you don't know the answer, just say that you don't know. \
    Use three sentences maximum and keep the answer concise.\

    {context}"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    return rag_chain