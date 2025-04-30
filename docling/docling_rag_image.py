import os
import json
import torch
from pathlib import Path
from tempfile import mkdtemp
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# Environment variables for Hugging Face cache and authentication
os.environ["TOKENIZERS_PARALLELISM"] = "false"
HF_TOKEN = "###"

# Model and database configuration
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
GEN_MODEL_ID = "mistralai/Mixtral-8x7B-Instruct-v0.1"
TOP_K = 3
IMAGE_RESOLUTION_SCALE = 2.0
MILVUS_URI = str(Path(mkdtemp()) / "docling.db")

# Define paths
PDF_FILE = "RA_2007_2_merged.pdf"
TXT_FILE = "RA_2007_2_merged_image.txt"
CACHE_DIR = "/scratch/project_2000539/maryam/embed/.cache"

def process_pdf(pdf_file, output_txt):
    """Converts the PDF to structured text and extracts images."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options.lang = ["ru"]
    pipeline_options.do_table_structure = True
    #pipeline_options.do_formula_understanding = True
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_picture_images = True
    
    doc_converter = DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
    )
    conv_result = doc_converter.convert(Path(pdf_file))
    doc_filename = conv_result.input.file.stem

    output_dir = Path("rag-img")
    output_dir.mkdir(parents=True, exist_ok=True)
    table_counter = 0
    picture_counter = 0
    for element, _level in conv_result.document.iterate_items():
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-table-{table_counter}.png"
            )
            image = element.get_image(conv_result.document)
            if image is None:
                print(f"Warning: No image found in for element {output_dir} / {doc_filename}-table-{table_counter}.png")
            else:
                with element_image_filename.open("wb") as fp:
                    image.save(fp, "PNG")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                output_dir / f"{doc_filename}-picture-{picture_counter}.png"
            )
            image = element.get_image(conv_result.document)
            if image is None:
                print(f"Warning: No image found for element {output_dir} / {doc_filename}-picture-{picture_counter}.png")
            else:
                with element_image_filename.open("wb") as fp:
                    image.save(fp, "PNG")

    # Save markdown with embedded pictures
    md_filename = output_dir / f"{doc_filename}-with-images.md"
    conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.EMBEDDED)

    # Save markdown with externally referenced pictures
    md_filename = output_dir / f"{doc_filename}-with-image-refs.md"
    conv_result.document.save_as_markdown(md_filename, image_mode=ImageRefMode.REFERENCED)

    with open(output_dir / output_txt, "w", encoding="utf-8") as file:
        file.write(json.dumps(conv_result.document.export_to_dict(), ensure_ascii=False, indent=2))
    
    return output_dir / output_txt

# Process the PDF file and extract text
TXT_FILE = process_pdf(PDF_FILE, TXT_FILE)

# Load local model and tokenizer
print("Loading the tokenizer")
tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL_ID, cache_dir=CACHE_DIR, token=HF_TOKEN)
print("Loading the model")
model = AutoModelForCausalLM.from_pretrained(GEN_MODEL_ID, cache_dir=CACHE_DIR, token=HF_TOKEN, device_map="auto", torch_dtype=torch.float16)
nlp_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Define RAG prompt
PROMPT = PromptTemplate.from_template(
    "Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context and images, answer the query.\nQuery: {input}\nAnswer:\n"
)

def extract_text_and_images(txt_file):
    """Parses the extracted text file to find references to images and tables."""
    with open(txt_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    text_sections = []
    image_references = []
    
    for item in data["body"]["children"]:
        if "text" in item:
            text_sections.append(item["text"])
        elif "pictures" in item:
            image_references.append(item)
    
    return "\n".join(text_sections), image_references


def retrieve_and_generate_answer(question):
    """Retrieves relevant text and images, then generates an answer."""
    embedding = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    vectorstore = Milvus.from_documents(
        documents=[Document(page_content=doc) for doc in text_content.split(".\n")],
        embedding=embedding,
        collection_name="docling_demo",
        connection_args={"uri": MILVUS_URI},
        index_params={"index_type": "FLAT"},
        drop_old=True,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": TOP_K})
    retrieved_docs = retriever.invoke(question)
    
    context_text = "\n".join([doc.page_content for doc in retrieved_docs])
    full_prompt = PROMPT.format(context=context_text, input=question)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token 
        
    inputs = tokenizer(full_prompt, return_tensors="pt", padding=True, truncation=True)
    input_ids = inputs.input_ids.to("cuda")
    attention_mask = inputs.attention_mask.to("cuda")
    output = model.generate(input_ids, attention_mask=attention_mask, pad_token_id=tokenizer.pad_token_id, max_length=200, num_return_sequences=1)
    answer = tokenizer.decode(output[0], skip_special_tokens=True)
    
    return answer, retrieved_docs


# Load text and images from the extracted document
text_content, image_refs = extract_text_and_images(TXT_FILE)

def main():
    question = "Какие факторы могут влиять на уровень изотопа 14C в образцах органического происхождения?"
    answer, retrieved_docs = retrieve_and_generate_answer(question)
    
    print(f"Question:\n{question}\n\nAnswer:\n{answer}")
    for i, doc in enumerate(retrieved_docs):
        print(f"\nSource {i+1}:\n  text: {doc.page_content}")
        if "pictures" in doc.metadata:
            print(f"  Image Reference: {doc.metadata['pictures']}")

    print("## text_content")
    print(text_content)
    print("## image refs")
    print(image_refs)

if __name__ == "__main__":
    main()
