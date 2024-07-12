import argparse
import os
import shutil

from tqdm import tqdm
from langchain.schema.document import Document

from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.document_loaders.pdf import PDFPlumberLoader
from typing import List, Union
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    parser = argparse.ArgumentParser(description="This script manages the database for the application. You can use it to clear the database, reset it, or populate it with a specific configuration that can be specified in the config.json file.")
    parser.add_argument("--config", type=str, help="Enter the name of the config you want to populate your database.")
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--clear", action="store_true", help="Clear the database.")

    args = parser.parse_args()

    if args.clear:
        print("✨ Clearing Database")
        if args.config:
            # Clear the specific subfolder specified in the config
            load_config(args.config)
            subfolder_name = "chroma_{}".format(EMBEDDING_MODEL)
            clear_database(subfolder_name)
        else:
            # Clear the whole database
            clear_database()
        return

    if args.config:
        load_config(args.config)
        if args.reset:
            # Clear the existing database existing for the specified config
            subfolder_name = "chroma_{}".format(EMBEDDING_MODEL)
            print("✨ Reseting Database")
            try:
                clear_database(subfolder_name)
            except FolderNotFoundError as e:
                print(e)

        # Create (or update) the data store.
        documents = load_documents()
        chunks = split_documents(documents)
        add_to_chroma(chunks)

def load_config(config_name):
    """
    Load and print the parameters entered for config_name into the config.json file.
    """
    global DATA_PATH, CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE
    from parameters import load_config as ld
    ld(config_name, show_config=True)
    from parameters import DATA_PATH, CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE   

def load_documents():
    """
    Load pdf documents with a langchain tool
    Load txt and docx with a llamaindex tool
    Convert everything in the same Document format

    #TODO Make something better maybe
    #TODO Implement other document type. llamaindex tool can do it
    """
    from llama_index.core import SimpleDirectoryReader

    langchain_documents = []
    llama_documents = []

    try:
        llama_document_loader = SimpleDirectoryReader(input_dir=DATA_PATH, required_exts=[".txt", ".docx"])
        for doc in tqdm(llama_document_loader.load_data(), desc="TXT/DOCX loaded"):
            doc.metadata.pop('file_path',None)
            print(doc.metadata)
            llama_documents.append(doc)
    except ValueError as e:
        print(e)

    langchain_document_loader = ProgressPyPDFDirectoryLoader(DATA_PATH)
    for doc in tqdm(langchain_document_loader.load(), desc="PDFs loaded"):
        print(doc.metadata)
        langchain_documents.append(doc)

    documents = langchain_documents + convert_llamaindexdoc_to_langchaindoc(llama_documents)
    print(f"Loaded {len(langchain_documents)} chunks from PDF documents, {len(llama_documents)} chunks from TXT/DOCX documents.\nTotal chunks: {len(documents)}.\n")
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
    from langchain_text_splitters import RecursiveCharacterTextSplitter
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
    from langchain.vectorstores.chroma import Chroma
    from get_embedding_function import get_embedding_function
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
    new_chunks = [chunk for chunk in chunks_with_ids if chunk.metadata["id"] not in existing_ids]
    batch_size = 1000

    if new_chunks:
        with tqdm(total=len(new_chunks), desc="Adding documents") as pbar:
            for i in range(0,len(new_chunks), batch_size):
                batch = new_chunks[i:i + batch_size]
                new_chunk_ids = [chunk.metadata["id"] for chunk in batch]
                db.add_documents(batch, ids=new_chunk_ids)
                db.persist()
                pbar.update(len(batch))

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

def find_chroma_path(model_name, base_path):
    """
    Find the path to the chroma database corresponding to the Embedding model
    Create the subfolder in the chroma root folder if not exists
    """
    if not model_name:
        raise ValueError("Model name can't be empty")

    if not base_path:
        try:
            base_path = CHROMA_ROOT_PATH
        except:
            raise ValueError("The Chroma database root file is not populated")
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
            raise FolderNotFoundError(f"Folder {full_path} doesn't exist")
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


class ProgressPyPDFDirectoryLoader(PyPDFDirectoryLoader):
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
                            for doc in sub_docs:
                                if 'source' in doc.metadata:
                                    doc.metadata['source'] = i.name
                                    doc.metadata['file_name'] = doc.metadata.pop('source')
                                doc.metadata.pop('file_path',None)
                                doc.metadata = {key: value for key, value in doc.metadata.items() if value}
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