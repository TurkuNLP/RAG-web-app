import argparse
import os
import shutil
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.vectorstores.chroma import Chroma
from llama_index.core import SimpleDirectoryReader

from parameters import DATA_PATH, CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE
from get_embedding_function import get_embedding_function

def main():
    # Check if the database should be cleared (using the --clear flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    args = parser.parse_args()
    if args.reset:
        print("✨ Clearing Database")
        clear_database()

    # Create (or update) the data store.
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_chroma(chunks)

def load_documents():
    """
    Load pdf documents with a langchain tool
    Load txt and docx with a llamaindex tool
    Convert everything in the same Document format

    #TODO Make something better maybe
    #TODO Implement other document type. llamaindex tool can do it
    """
    langchain_document_loader = PyPDFDirectoryLoader(DATA_PATH)
    langchain_documents = langchain_document_loader.load()
    llama_document_loader = SimpleDirectoryReader(input_dir=DATA_PATH, required_exts=[".txt", ".docx"])
    llama_documents = llama_document_loader.load_data()
    documents = langchain_documents + convert_llamaindexdoc_to_langchaindoc(llama_documents)
    print(len(langchain_documents), len(llama_documents), len(documents))
    return documents

def convert_llamaindexdoc_to_langchaindoc(documents: list[Document]):
    """
    Convert documents from llamaindex library into the same format as those in langchain, so that you can create a single list
    """
    langchain_docs = []
    for doc in documents:
        metadata = {"source" : doc.metadata["file_name"], "page" : "N/A"}
        langchain_docs.append(Document(page_content=doc.text, metadata=metadata))
    return langchain_docs

def split_documents(documents: list[Document]):
    """
    Split documents into smaller chunks
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    """
    Load the chroma database
    Check if there are new documents in the documents database
    Add them to the chroma database
    """
    # Load the existing database.
    db = Chroma(
        persist_directory=find_chroma_path(EMBEDDING_MODEL,CHROMA_ROOT_PATH), embedding_function=get_embedding_function(EMBEDDING_MODEL)
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    """
    Add metadata id to the chunk in the following format:
    document_name.extension:page_number:chunk_number
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = str(chunk.metadata.get("page"))
        current_page_id = f"{source}:page={page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id
    return chunks

def find_chroma_path(model_name, base_path = CHROMA_ROOT_PATH):
    """
    Find the path to the chroma database corresponding to the Embedding model
    Create the subfolder in the chroma root folder if not exists
    """
    if not model_name:
        raise ValueError("Model name can't be empty")
    # Set model_path
    model_path = os.path.join(base_path, f"chroma_{model_name}")
    if not os.path.exists(model_path):
        # Create folder if doesn't exist
        os.makedirs(model_path)
    return model_path

def clear_database(chroma_subfolder_name = None):
    """
    Clear the folder if chroma_subfolder_name is set and exists
    Clear the whole database if not set but ask the user before
    """
    if chroma_subfolder_name:
        full_path = os.path.join(CHROMA_ROOT_PATH, chroma_subfolder_name)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"The database in {full_path} has been successfully deleted.")
        else:
            raise ValueError(f"Folder {full_path} doesn't exist")
    else:
        print("\nExisting databases :\n\n")
        subfolders = [f for f in os.listdir(CHROMA_ROOT_PATH) if os.path.isdir(os.path.join(CHROMA_ROOT_PATH, f))]
        if not subfolders:
            print(f"no subfolder found in {CHROMA_ROOT_PATH}\n\n")
        for subfolder in subfolders:
            print(f"- {subfolder}")
        
        confirmation = input("Do you want to delete all the databases ? (yes/no) : ")
        if confirmation.lower() == 'yes':
            shutil.rmtree(CHROMA_ROOT_PATH)
            print("All databases cleared")
        else:
            print("Deletion cancelled.")

if __name__ == "__main__":
    main()