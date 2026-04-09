import os
import sys
import time
import logging
import json
import threading

from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
law_app = Flask(__name__, template_folder="../templates", static_folder="../static")


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python_script')))
from parameters import load_config
global DATA_PATH
load_config('law')
from parameters import DATABASE_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE, DATA_PATH, REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT
from get_llm_function import get_llm_function
from get_rag_chain import get_rag_chain
from ConversationalRagChain import ConversationalRagChain

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if not os.path.isabs(DATA_PATH):
    DATA_PATH = os.path.join(APP_ROOT, DATA_PATH)


root = "/law"

@law_app.route("/")
def index():
    return render_template('law_index.html', root=root)


def init_app():
    load_rag()
    law_app.config['UPLOAD_FOLDER'] = DATA_PATH


def load_rag(settings = None):
    global rag_conv
    if settings is None :
        rag_conv = ConversationalRagChain.from_llm(
            rag_chain=get_rag_chain(),
            llm=get_llm_function(model_name = LLM_MODEL),
            callbacks=None
        )
    else:
        rag_conv = ConversationalRagChain.from_llm(
            rag_chain=get_rag_chain(settings),
            llm=get_llm_function(model_name = settings["llm_model"]),
            callbacks=None
        )


# Route to get the document list
@law_app.route('/documents', methods=['GET'])
def list_documents():
    files = os.listdir(law_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"{root}/files/{f}", "extension": os.path.splitext(f)[1][1:]} for f in files]
    return jsonify(documents)


# Route to get a single document
@law_app.route('/documents/<document_name>', methods=['GET'])
def get_document(document_name):
    files = os.listdir(law_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"{root}/files/{f}", "extension": os.path.splitext(f)[1][1:]} for f in files]
    
    document = next((doc for doc in documents if doc["name"] == document_name), None)
    
    if document is None:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document)

# Route to show the pdf
@law_app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(law_app.config['UPLOAD_FOLDER'], filename)


@law_app.route("/get", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("msg", "")
    return stream_chat_response(msg)

def compute_chat_response(query):
    start_time = time.perf_counter()
    logging.info("RAG /get start")
    inputs = {
    "query": str(query),
    "chat_history": []
    }
    res = rag_conv._call(inputs)
    duration_s = time.perf_counter() - start_time
    logging.info("RAG /get done in %.3fs", duration_s)

    output = {
        'response': res['result'],
        'context': res['context'],
        'metadatas': res['metadatas']
    }
    return output

def stream_chat_response(query):
    result = {"done": False, "payload": None}

    def run_query():
        try:
            result["payload"] = compute_chat_response(query)
        except Exception as exc:
            logging.exception("RAG /get failed")
            result["payload"] = {
                "response": f"Server error: {exc}",
                "context": [],
                "metadatas": []
            }
        result["done"] = True

    thread = threading.Thread(target=run_query, daemon=True)
    thread.start()

    def generate():
        while not result["done"]:
            yield " \n"
            time.sleep(5)
        yield json.dumps(result["payload"])

    return Response(
        stream_with_context(generate()),
        mimetype="application/json",
        headers={"X-Accel-Buffering": "no"},
    )
    return output


@law_app.route('/update-settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    load_rag(settings=data)
    return jsonify({'status': 'success', 'message': 'Settings updated successfully'}), 200


@law_app.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    rag_conv.clear_chat_history()
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    init_app()
    law_app.run(port=6670,debug=False)
