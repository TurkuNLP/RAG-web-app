from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL

from get_embedding_function import get_embedding_function
from get_llm_function import get_llm_function
from populate_database import find_chroma_path

from langchain.vectorstores.chroma import Chroma
from langchain.chains import create_history_aware_retriever
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_rag_chain(retrieved_doc_nb = 5, params = None):
    default_params = {
        "CHROMA_ROOT_PATH": CHROMA_ROOT_PATH,
        "EMBEDDING_MODEL": EMBEDDING_MODEL,
        "LLM_MODEL": LLM_MODEL,
    }
    if params is None :
        params = default_params
    else:
        params = {**default_params, **params}

    try:
        embedding_model = get_embedding_function(model_name=EMBEDDING_MODEL)
        llm = get_llm_function(model_name=LLM_MODEL)
        db = Chroma(persist_directory=find_chroma_path(model_name=EMBEDDING_MODEL, base_path=CHROMA_ROOT_PATH), embedding_function=embedding_model)
    except NameError as e:
        variable_name = str(e).split("'")[1]
        raise NameError (f"The global variable '{variable_name}' is not defined. Please ensure that all required global variables (EMBEDDING_MODEL, LLM_MODEL, CHROMA_ROOT_PATH) are imported or defined.") from e
    
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": retrieved_doc_nb})


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

    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    return rag_chain