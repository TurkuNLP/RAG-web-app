import openai
import json
import re
import os

# OpenAI API key (Replace with your key)
api_key = os.environ["OPENAI_API_KEY"]

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
                chunks.append(current_chunk.strip())  # Store completed chunk
                current_chunk = section  # Start a new chunk
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

def main():

    # Load the Markdown file
    file_path = "data/documents/ship_processed/md-ref/216(82)_Amendments to SOLAS-with-image-refs.md"

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Split text into chunks (preserving section context)
    sections = re.split(r"\n## ", content)
    sections = ["## " + sec.strip() for sec in sections if sec.strip()]

    text_chunks = get_chunks(sections)
    # Generate QA pairs from each chunk
    qa_pairs = []
    for chunk in text_chunks[:50]:  # Limit batch size for testing
        try:
            qa = generate_qa(chunk)
            qa_pairs.append({"question": qa["question"], "answer": qa["answer"]})
        except Exception as e:
            print(f"Error processing chunk: {str(e)}")

    # Save to JSONL format
    qa_corpus_path = "generated_qa_corpus.jsonl"
    with open(qa_corpus_path, "w", encoding="utf-8") as jsonl_file:
        for qa in qa_pairs:
            jsonl_file.write(json.dumps(qa, ensure_ascii=False) + "\n")

    print(f"QA corpus saved at {qa_corpus_path}")

main()
