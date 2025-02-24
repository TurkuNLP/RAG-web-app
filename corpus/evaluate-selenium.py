from sentence_transformers import SentenceTransformer, util
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configurations
RAG_URL = "https://rag.turkunlp.org/seus"
RESULTS_PATH = "data/documents/ship_processed/test-responds"
MAX_TESTS = 50  # Number of questions to test
SOURCE = "data/documents/ship_processed/QA"

# Load sentence embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")  # Lightweight & fast

def compute_similarity(text1, text2):
    """Compute cosine similarity between two texts using embeddings."""
    if not text1 or not text2:
        return 0.0  # If either response is empty, similarity is 0
    
    emb1 = embedding_model.encode(text1, convert_to_tensor=True)
    emb2 = embedding_model.encode(text2, convert_to_tensor=True)

    return util.pytorch_cos_sim(emb1, emb2).item()  # Convert to float

def setup_driver():
    """Setup Selenium WebDriver for a remote system (headless mode)."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")  
    options.add_argument("--disable-gpu")  
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--remote-debugging-port=9222")  
    options.binary_location = "/usr/bin/chromium-browser"

    service = Service("/usr/local/bin/chromedriver")  
    driver = webdriver.Chrome(service=service, options=options)

    return driver

def send_query_with_selenium(driver, question):
    """Send a question using Selenium and capture the dynamic response."""
    driver.get(RAG_URL)  

    try:
        chat_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "chatInput"))
        )
        chat_input.send_keys(question)

        send_button = driver.find_element(By.ID, "send-btn")
        driver.execute_script("arguments[0].scrollIntoView(true);", send_button)
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "send-btn")))

        try:
            send_button.click()
        except:
            driver.execute_script("arguments[0].click();", send_button)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.chatbox li.message.incoming"))
        )
        messages = driver.find_elements(By.CSS_SELECTOR, "ul.chatbox li.message.incoming")
        latest_response = messages[-1].text if messages else None  

        return latest_response

    except Exception as e:
        print(f"⚠️ Error processing query: {e}")
        return None

def test_rag(QA_file, driver):
    """Test the RAG web app using the generated QA dataset."""
    with open(QA_file, "r", encoding="utf-8") as file:
        qa_pairs = [json.loads(line) for line in file]

    test_results = []
    correct_count = 0
    for idx, qa in enumerate(qa_pairs[:MAX_TESTS]):  
        question = qa["question"]
        expected_answer = qa["answer"]

        print(f"🔹 Testing Question {idx+1}: {question}")
        
        response_text = send_query_with_selenium(driver, question)

        # Compute semantic similarity
        similarity_score = compute_similarity(expected_answer, response_text)
        threshold = 0.7  # Consider it correct if similarity is above 0.7

        correct = similarity_score >= threshold

        if correct:
            correct_count += 1  

        result = {
            "question": question,
            "expected_answer": expected_answer,
            "actual_response": response_text,
            "similarity_score": similarity_score,
            "correct": correct
        }
        test_results.append(result)

        print(f"✅ Result: {'PASS' if correct else 'FAIL'} (Similarity: {similarity_score:.2f})")
        time.sleep(1)  

    os.makedirs(RESULTS_PATH, exist_ok=True)
    qa_corpus = ".jsonl"
    file_name = os.path.splitext(os.path.basename(QA_file))[0]
    out_path = os.path.join(RESULTS_PATH, f"{file_name}{qa_corpus}")

    with open(out_path, "w", encoding="utf-8") as file:
        for result in test_results:
            file.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"Results saved to {out_path}")

    return correct_count, len(test_results)

def main():
    """Process all QA files and run tests"""
    driver = setup_driver()
    QA_total = 0
    QA_correct = 0

    for filename in os.listdir(SOURCE):
        file_path = os.path.join(SOURCE, filename)
        correct, total = test_rag(file_path, driver)

        QA_correct += correct
        QA_total += total  

    driver.quit() 

    print(f"\n📌 Testing complete. {QA_correct}/{QA_total} questions answered correctly.")

if __name__ == "__main__":
    main()
