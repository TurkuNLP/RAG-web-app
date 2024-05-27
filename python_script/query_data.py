from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate

from get_embedding_function import get_embedding_function
from get_llm_function import get_llm_function
from populate_database import find_chroma_path
from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_model = get_embedding_function(EMBEDDING_MODEL)
    db = Chroma(persist_directory=find_chroma_path(EMBEDDING_MODEL,CHROMA_ROOT_PATH), embedding_function=embedding_model)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    sources = [doc.metadata.get("id", None) for doc, _score in results]

    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    llm_model = get_llm_function(LLM_MODEL)
    
    raw_response_text = llm_model.invoke(prompt)
    formated_response_text = format_response(raw_response_text, query_text)
    return formated_response_text, context_text, sources

def format_response(response_text, query_text):
    if LLM_MODEL == "gpt-3.5-turbo":
        return response_text.content
    
    elif LLM_MODEL == "mistralai/Mixtral-8x7B-Instruct-v0.1":
        answer_start_index = response_text.find("Answer: ")
        if answer_start_index != -1:
            answer = response_text[answer_start_index + len("Answer :"):].strip()
        else:
            answer = "Response not found"       
        return answer
    
    elif LLM_MODEL == "mistralai/Mistral-7B-Instruct-v0.1":
        answer_start_index = response_text.find("Answer the question based on the above context: ")
        if answer_start_index != -1:
            answer = response_text[answer_start_index + len("Answer the question based on the above context: ") + len(query_text):].strip()
        else:
            answer = "Response not found"
        return answer
    
    elif LLM_MODEL == "nvidia/Llama3-ChatQA-1.5-8B":
        return response_text
    
    else:
        raise ValueError(f"LLM model '{LLM_MODEL}' isn't configure or doesn't exist")

def main():
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, help="The query text.")
    args = parser.parse_args()
    query_text = args.query_text
    query_rag(query_text)
    """
    all_question_data = ["What is the maximum possible vertical extent of damage above the baseline?","How do you express the index A of probability of surviving after collision damage?","What criteria are used to identify 'large lower holds' in a ship, particularly in terms of the horizontal surfaces and their relationship to the waterplane area at subdivision draught?","When is it permissible to use alternative figures for permeability in ship design, and what criteria must be met for such recalculations to be considered?","How is the value of sfinal determined if the equalization time exceeds 10 minutes?","What considerations should be taken into account when determining the subdivision of a ship's hull, particularly in relation to achieving a high attained index A?","How are the GM (or KG) values initially determined for the three loading conditions, and what steps are taken if the required index R is not achieved?"]

    for i in range(1):
        query_text = all_question_data[i]
        response_text, context_text, source_text = query_rag("Quel est le filtre de Sobel ?")
        print("========== Réponse ===========\n\n")
        print(response_text)
        print("\n\n========== context ===========\n\n")
        print(context_text)
        print("\n\n========== sources ===========\n\n")
        print(source_text)

if __name__ == "__main__":
    main()
