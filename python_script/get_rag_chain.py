from langchain.vectorstores.chroma import Chroma
from langchain.chains import RetrievalQA

from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE

from get_embedding_function import get_embedding_function
from get_llm_function import get_llm_function
from populate_database import find_chroma_path

def get_rag_chain():
    """Get the rag chain"""
    embedding_model = get_embedding_function(EMBEDDING_MODEL)

    db = Chroma(persist_directory=find_chroma_path(EMBEDDING_MODEL,CHROMA_ROOT_PATH), embedding_function=embedding_model)

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    
    qa = RetrievalQA.from_chain_type(
        llm=get_llm_function(LLM_MODEL),
        retriever=retriever,
        return_source_documents=True,
        verbose=False,
        chain_type_kwargs={"prompt": PROMPT_TEMPLATE}
    )
    return qa