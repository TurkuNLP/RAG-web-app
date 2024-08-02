import os
import sys

from flask import Flask, Blueprint, render_template, request, jsonify, send_from_directory, url_for

arch_en = Flask(__name__)
main = Blueprint('main', __name__, static_folder='static', static_url_path='/arch-en/static', template_folder='templates')


sys.path.append(os.path.join(os.path.dirname(__file__), 'python_script'))
from parameters import load_config
global DATA_PATH
load_config('arch_en')
from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE, DATA_PATH, REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT
from get_llm_function import get_llm_function
from get_rag_chain import get_rag_chain
from ConversationalRagChain import ConversationalRagChain

@arch_en.route("/")
def index():
    root = "arch-en"
    return render_template('arch_en_index.html', root=root)


def init_app():
    load_rag()
    arch_en.config['UPLOAD_FOLDER'] = DATA_PATH


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
@arch_en.route('/documents', methods=['GET'])
def list_documents():
    files = os.listdir(arch_en.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"/arch-en/files/{f}", "extension":os.path.splitext(f)[1][1:]} for f in files]
    return jsonify(documents)


# Route to get a single document
@arch_en.route('/documents/<document_name>', methods=['GET'])
def get_document(document_name):
    files = os.listdir(arch_en.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"/arch-en/files/{f}", "extension": os.path.splitext(f)[1][1:]} for f in files]
    
    document = next((doc for doc in documents if doc["name"] == document_name), None)
    
    if document is None:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document)


# Route to show the pdf
@arch_en.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(arch_en.config['UPLOAD_FOLDER'], filename)


@arch_en.route("/get", methods=["POST"])
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

    output = jsonify({
        'response': res['result'],
        'context': res['context'],
        'metadatas': res['metadatas']
    })
    return output


@arch_en.route('/update-settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    load_rag(settings=data)
    return jsonify({'status': 'success', 'message': 'Settings updated successfully'}), 200


@arch_en.route('/clear_chat_history', methods=['POST'])
def clear_chat_history():
    rag_conv.clear_chat_history()
    return jsonify({"status": "success"}), 200


if __name__ == '__main__':
    init_app()
    arch_en.run(port=6668,debug=False)