import os
from pathlib import Path
from tempfile import mkdtemp
import json

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_docling.loader import ExportType

from langchain_docling import DoclingLoader
from docling.chunking import HybridChunker
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEndpoint

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
    TesseractOcrOptions,
    AcceleratorDevice,
    AcceleratorOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption


import logging
import time
_log = logging.getLogger(__name__)


os.environ["TORCH_EXTENSIONS_DIR"] = "/scratch/project_2000539/maryam/embed/.cache/torch_extensions_cache"
os.environ["HF_HOME"] = "/scratch/project_2000539/maryam/embed/.cache/hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/scratch/project_2000539/maryam/embed/.cache/hf_cache"


def _get_env_from_colab_or_os(key):
    try:
        from google.colab import userdata

        try:
            return userdata.get(key)
        except userdata.SecretNotFoundError:
            pass
    except ImportError:
        pass
    return os.getenv(key)


load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

HF_TOKEN = _get_env_from_colab_or_os("HF_TOKEN") #
FILE_PATH = ["/scratch/project_2000539/maryam/adaptive-mrag/RA_2007_2.pdf"]  
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
EXPORT_TYPE = ExportType.DOC_CHUNKS
QUESTION = "Какие факторы могут влиять на уровень изотопа 14C в образцах органического происхождения?"
PROMPT = PromptTemplate.from_template(
    "Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {input}\nAnswer:\n",
)
TOP_K = 3
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")


def main():

    logging.basicConfig(level=logging.INFO)
    input_doc_path = Path("/scratch/project_2000539/maryam/adaptive-mrag/RA_2007_2.pdf")
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.do_table_structure = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.ocr_options.lang = ["ru"]
    pipeline_options.accelerator_options = AcceleratorOptions(
        num_threads=4, device=AcceleratorDevice.AUTO
    )

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()
    conv_result = doc_converter.convert(input_doc_path)
    end_time = time.time() - start_time

    _log.info(f"Document converted in {end_time:.2f} seconds.")

    output_dir = Path("scratch")
    output_dir.mkdir(parents=True, exist_ok=True)
    doc_filename = conv_result.input.file.stem

    # Export Deep Search document JSON format:
    with (output_dir / f"{doc_filename}.txt").open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(conv_result.document.export_to_dict()))

    # Set lang=["auto"] with a tesseract OCR engine: TesseractOcrOptions, TesseractCliOcrOptions
    #ocr_options = TesseractOcrOptions(lang=["auto"])
    ocr_options = TesseractCliOcrOptions(lang=["auto"])

    pipeline_options = PdfPipelineOptions(
        do_ocr=True, force_full_page_ocr=True, ocr_options=ocr_options
    )
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options,
            )
        }
    )

    loader = DoclingLoader(
        file_path=FILE_PATH,
        #converter=converter,
        export_type=EXPORT_TYPE,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID),
    )

    docs = loader.load()
    print("doc loaded")
    if EXPORT_TYPE == ExportType.DOC_CHUNKS:
        splits = docs
    elif EXPORT_TYPE == ExportType.MARKDOWN:
        from langchain_text_splitters import MarkdownHeaderTextSplitter

        splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header_1"),
                ("##", "Header_2"),
                ("###", "Header_3"),
            ],
        )
        splits = [split for doc in docs for split in splitter.split_text(doc.page_content)]
    else:
        raise ValueError(f"Unexpected export type: {EXPORT_TYPE}")
    

    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)


    milvus_uri = str(Path(mkdtemp()) / "docling.db")  # or set as needed
    vectorstore = Milvus.from_documents(
        documents=splits,
        embedding=embedding,
        collection_name="docling_demo",
        connection_args={"uri": milvus_uri},
        index_params={"index_type": "FLAT"},
        drop_old=True,
    )


    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    llm = HuggingFaceEndpoint(
        repo_id=GEN_MODEL_ID,
        huggingfacehub_api_token=HF_TOKEN,
        task="text-generation"
    )


    def clip_text(text, threshold=100):
        return f"{text[:threshold]}..." if len(text) > threshold else text
    print("before chain")
    question_answer_chain = create_stuff_documents_chain(llm, PROMPT)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    resp_dict = rag_chain.invoke({"input": QUESTION})

    clipped_answer = clip_text(resp_dict["answer"], threshold=200)
    print(f"Question:\n{resp_dict['input']}\n\nAnswer:\n{clipped_answer}")
    for i, doc in enumerate(resp_dict["context"]):
        print()
        print(f"Source {i+1}:")
        print(f"  text: {json.dumps(clip_text(doc.page_content, threshold=350))}")
        for key in doc.metadata:
            if key != "pk":
                val = doc.metadata.get(key)
                clipped_val = clip_text(val) if isinstance(val, str) else val
                print(f"  {key}: {clipped_val}")

main()