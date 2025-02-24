import openai
import json
import re
import os
import numpy as np

api_key = os.environ["OPENAI_API_KEY"]
SOURCE = "data/documents/ship_processed/md-ref"
OUT_DIR = "data/documents/ship_processed/QA"
API_LIMIT = 8000 # Just to be safe, original MAX is 12800 

def get_chunks(sections):

    # Improved Chunking: Merge consecutive small sections
    chunks = []
    current_chunk = ""
    token_limit = 1000  # Approximate character-based token limit

    for section in sections:
        if len(section.split()) < 50:  # If section is too small (e.g., just a title)
            current_chunk += "\n\n" + section  # Merge with previous chunk
        else:
            if len(current_chunk) > token_limit:
                if len(current_chunk) < API_LIMIT:
                    chunks.append(current_chunk.strip())  # Store completed chunk
                    current_chunk = section  # Start a new chunk
                else:
                    start = 0
                    for ch in range(0,len(current_chunk),API_LIMIT):
                        chunks.append(current_chunk[start:ch])
                        start = ch
                    current_chunk = section
            else:
                current_chunk += "\n\n" + section  # Append to current chunk

    # Add last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# Function to generate questions using GPT-4
def generate_qa(text_chunk):
    prompt = f"""
    Given the following document excerpt:

    {text_chunk}

    Generate exactly **one** question based on this text.
    The question can be of **any one** of these types:
    - **Factual** (What, When, Where)
    - **Explanatory** (Why, How)
    - **Application-based** (How does X impact Y?)

    Then, generate a short, clear **answer** to the question based on the provided text.

    Ensure the response is a **valid JSON object** with two fields:
    {{
        "question": "Your generated question here",
        "answer": "Your generated answer here"
    }}

    **IMPORTANT**: Do NOT include anything else in the response. Only return the JSON object.
    """


    client = openai.OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an AI assistant that generates precise Q&A pairs."},
                  {"role": "user", "content": prompt}]
    )

    return json.loads(response.choices[0].message.content)

def process_file(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split text into chunks (preserving section context)
    sections = re.split(r"\n## ", content)
    sections = ["## " + sec.strip() for sec in sections if sec.strip()]

    text_chunks = get_chunks(sections)

    # Determine how many chunks to sample
    total_chunks = len(text_chunks)
    num_samples = min(10, max(3, total_chunks // 10))  # At least 3, at most 10

    # Select `num_samples` chunks evenly spaced across the document
    selected_indices = np.linspace(0, total_chunks - 1, num_samples, dtype=int)
    sampled_chunks = [text_chunks[i] for i in selected_indices]

    # Generate QA pairs from each chunk
    qa_pairs = []
    for chunk in sampled_chunks:
        try:
            qa = generate_qa(chunk)
            qa_pairs.append({"question": qa["question"], "answer": qa["answer"]})
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")

    # Save to JSONL format
    qa_corpus = "qa.jsonl"
    file_name = os.path.splitext(os.path.basename(file_path))[0]
    with open(os.path.join(OUT_DIR, f"{file_name}-{qa_corpus}"), "w", encoding="utf-8") as jsonl_file:
        for qa in qa_pairs:
            jsonl_file.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"QA corpus saved at ", os.path.join(OUT_DIR, f"{file_name}-{qa_corpus}"))


def main():

    for filename in os.listdir(SOURCE):
        if not filename.endswith(".md"):
            continue
        file_path = os.path.join(SOURCE, filename)
        process_file(file_path)
    
main()