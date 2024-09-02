import argparse
import os
import shutil

from tqdm import tqdm
import faiss
from typing import List
from pathlib import Path
import logging

from get_embedding_function import get_embedding_function

from langchain.schema.document import Document
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.document_loaders.pdf import PDFPlumberLoader
from llama_index.core import SimpleDirectoryReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="""This script manages the database for the application.
                                    You can use it to clear the database, reset it, or populate 
                                    it with a specific configuration that can be specified in the
                                    config.json file.""")
    parser.add_argument("--config", type=str, help="Enter the name of the config you want to populate your database.")
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--clear", action="store_true", help="Clear the database.")

    args = parser.parse_args()

    if args.clear:
        print("Clearing Database...")
        if args.config:
            load_config(args.config)
            subfolder_name = "database_{}".format(EMBEDDING_MODEL)
            clear_database(subfolder_name)
        else:
            clear_database()
        return

    if args.config:
        load_config(args.config)
        if args.reset:
            subfolder_name = "database_{}".format(EMBEDDING_MODEL)
            print("Reseting Database...")
            try:
                clear_database(subfolder_name)
            except FolderNotFoundError as e:
                print(e)

        documents = load_documents()
        chunks = split_documents(documents)
        add_to_database(chunks)

def add_to_database(chunks: list[Document]):

    # Assume all valid embeddings have the same dimension
    index = faiss.IndexFlatL2(len(get_embedding_function(EMBEDDING_MODEL).embed_query("hello world")))

    vector_store = FAISS(
        embedding_function=get_embedding_function(EMBEDDING_MODEL),
        index=index,
        docstore= InMemoryDocstore(),
        index_to_docstore_id={}
    )
    existing_ids = []
    
    index_file = find_database_path(EMBEDDING_MODEL,DATABASE_ROOT_PATH) + "index.faiss"
    if os.path.exists(index_file):
        vector_store = FAISS.load_local(find_database_path(EMBEDDING_MODEL,DATABASE_ROOT_PATH),
                                        get_embedding_function(EMBEDDING_MODEL), 
                                        allow_dangerous_deserialization=True)
        # Add or Update the documents.
        existing_ids = vector_store.index_to_docstore_id.values()
        print("existing_ids", vector_store.index_to_docstore_id.values())

    chunks_with_ids = calculate_chunk_ids(chunks)

    # Only add documents that don't exist in the DB.
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]
    batch_size = 1000

    if new_chunks:
        with tqdm(total=len(new_chunks), desc="Adding chunks") as pbar:
            for i in range(0,len(new_chunks), batch_size):
                batch = new_chunks[i:i + batch_size]
                new_chunk_ids = [chunk.metadata["id"] for chunk in batch]
                vector_store.add_documents(batch, ids=new_chunk_ids)
                pbar.update(len(batch))
    
    vector_store.save_local(find_database_path(EMBEDDING_MODEL,DATABASE_ROOT_PATH))

def load_config(config_name):
    """
    Load and print the parameters entered for config_name into the config.json file.
    """
    global DATA_PATH, DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE
    from parameters import load_config as ld
    ld(config_name, show_config=True)
    from parameters import DATA_PATH, DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE   

def load_documents():
    """
    Load pdf documents with a langchain tool
    Load txt and docx with a llamaindex tool
    Convert everything in the same Document format

    #TODO Make something better maybe
    #TODO Implement other document type. llamaindex tool can do it
    """

    langchain_documents = []
    llama_documents = []

    try:
        llama_document_loader = SimpleDirectoryReader(input_dir=DATA_PATH, required_exts=[".txt", ".docx"])
        for doc in tqdm(llama_document_loader.load_data(), desc="TXT/DOCX loaded"):
            doc.metadata.pop('file_path',None)
            llama_documents.append(doc)
    except ValueError as e:
        print(e)

    langchain_document_loader = ProgressPyPDFDirectoryLoader(DATA_PATH)
    for doc in tqdm(langchain_document_loader.load(), desc="PDFs loaded"):
        doc.metadata.pop('file_path',None)
        langchain_documents.append(doc)

    documents = langchain_documents + convert_llamaindexdoc_to_langchaindoc(llama_documents)
    print(f"Loaded {len(langchain_documents)} page{'s' if len(langchain_documents) > 1 else ''} from PDF document{ \
        's' if len(langchain_documents) > 1 else ''}, {len(llama_documents)} item{'s' \
            if len(llama_documents) > 1 else ''} from TXT/DOCX document{'s' if len(llama_documents) > 1 else ''}.\nTotal items: {len(documents)}.\n")
    return documents

def convert_llamaindexdoc_to_langchaindoc(documents: list[Document]):
    """
    Convert documents from llamaindex library into the same format as those in langchain, so that you can create a single list
    """
    langchain_docs = []
    for doc in documents:
        langchain_docs.append(Document(page_content=doc.text, metadata=doc.metadata))
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

def calculate_chunk_ids(chunks):
    """
    Add metadata id to the chunk in the following format:
    document_name.extension:page_number:chunk_number
    """
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("file_name")
        page = str(chunk.metadata.get("page"))
        current_page_id = f"{source}:p{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:c{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id
    return chunks

def find_database_path(model_name, base_path):
    """
    Find the path to the database corresponding to the Embedding model
    Create the subfolder in the database root folder if not exists
    """
    if not model_name:
        raise ValueError("Model name can't be empty")

    if not base_path:
        try:
            base_path = DATABASE_ROOT_PATH
        except:
            raise ValueError("The database database root file is not populated")
        
    model_path = os.path.join(base_path, f"database_{model_name}")
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    return model_path

def clear_database(database_subfolder_name = None):
    """
    Clear the folder if database_subfolder_name is set and exists
    Clear the whole database if not set but ask the user before
    """
    if database_subfolder_name:
        full_path = os.path.join(DATABASE_ROOT_PATH, database_subfolder_name)
        if os.path.exists(full_path):
            shutil.rmtree(full_path)
            print(f"The database in {full_path} has been successfully deleted.")
        else:
            raise FolderNotFoundError(f"Folder {full_path} doesn't exist")
    else:
        print("\nExisting databases :\n\n")
        subfolders = [f for f in os.listdir(DATABASE_ROOT_PATH) if os.path.isdir(os.path.join(DATABASE_ROOT_PATH, f))]
        if not subfolders:
            print(f"no subfolder found in {DATABASE_ROOT_PATH}\n\n")
        for subfolder in subfolders:
            print(f"- {subfolder}")
        
        confirmation = input("Do you want to delete all the databases ? (yes/no) : ")
        if confirmation.lower() == 'yes':
            shutil.rmtree(DATABASE_ROOT_PATH)
            print("All databases cleared")
        else:
            print("Deletion cancelled.")


class ProgressPyPDFDirectoryLoader(PyPDFDirectoryLoader):
    """
    Custom PyPDFDirectoryLoader that changes the basic loader to PDFPlumberLoader which allow us to get all the metadata
    """
    def load(self) -> List[Document]:
        p = Path(self.path)
        docs = []
        items = list(p.rglob(self.glob)) if self.recursive else list(p.glob(self.glob))
        
        with tqdm(total=len(items), desc="Loading PDFs") as pbar:
            for i in items:
                if i.is_file():
                    if self._is_visible(i.relative_to(p)) or self.load_hidden:
                        try:
                            loader = PDFPlumberLoader(str(i), extract_images=self.extract_images)
                            sub_docs = loader.load()
                            page_counter = 1
                            for doc in sub_docs:
                                if 'source' in doc.metadata:
                                    doc.metadata['source'] = i.name
                                    doc.metadata['file_name'] = doc.metadata.pop('source')
                                doc.metadata = {key: value for key, value in doc.metadata.items() if value}
                                doc.metadata['page_counter'] = page_counter
                                page_counter += 1
                            docs.extend(sub_docs)
                        except Exception as e:
                            if self.silent_errors:
                                logger.warning(e)
                            else:
                                raise e
                pbar.update(1)
        return docs

class FolderNotFoundError(Exception):
    """Exception raised when a folder is not found."""
    pass

if __name__ == "__main__":
    main()