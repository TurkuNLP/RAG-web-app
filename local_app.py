import os
import sys

from flask import Flask, render_template, request, jsonify, send_from_directory
local_app = Flask(__name__)


sys.path.append(os.path.join(os.path.dirname(__file__), 'python_script'))
from parameters import load_config
global DATA_PATH
load_config('test')
from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE, DATA_PATH, REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT
from get_llm_function import get_llm_function
from get_rag_chain import get_rag_chain
from ConversationalRagChain import ConversationalRagChain


root = ""


@local_app.route("/")
def index():
    return render_template('local.html', root=root)


def init_app():
    load_rag()
    local_app.config['UPLOAD_FOLDER'] = DATA_PATH


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
@local_app.route('/documents', methods=['GET'])
def list_documents():
    files = os.listdir(local_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"{root}/files/{f}", "extension":os.path.splitext(f)[1][1:]} for f in files]
    return jsonify(documents)


# Route to get a single document
@local_app.route('/documents/<document_name>', methods=['GET'])
def get_document(document_name):
    files = os.listdir(local_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"{root}/files/{f}", "extension": os.path.splitext(f)[1][1:]} for f in files]
    
    document = next((doc for doc in documents if doc["name"] == document_name), None)
    
    if document is None:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document)

# Route to show the pdf
@local_app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(local_app.config['UPLOAD_FOLDER'], filename)

@local_app.route("/get", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("msg", "")
    return get_Chat_response(msg)

def get_Chat_response(query):
    inputs = {
    "query": str(query),
    "chat_history": []
    }
    res = rag_conv._call(inputs)
    print(res['metadatas'])
    output = jsonify({
        'response': res['result'],
        'context': res['context'],
        'metadatas': res['metadatas']
    })
    return output


@local_app.route('/update-settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    load_rag(settings=data)
    return jsonify({'status': 'success', 'message': 'Settings updated successfully'}), 200


@local_app.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    rag_conv.clear_chat_history()
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    init_app()
    local_app.run(port=5000,debug=True)