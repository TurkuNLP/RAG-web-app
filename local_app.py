import os
import sys

from flask import Flask, render_template, request, jsonify, send_from_directory

local_app = Flask(__name__)

def init_app():
    local_app.config['UPLOAD_FOLDER'] = "document"
    load_rag()

def load_rag():
    sys.path.append(os.path.join(os.path.dirname(__file__), 'python_script'))
    from parameters import load_config
    load_config('test')

    from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE, DATA_PATH, REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT
    from get_llm_function import get_llm_function
    from get_rag_chain_V2 import get_rag_chain
    from ConversationalRagChainV2 import ConversationalRagChain

    global rag_conv

    rag_conv = ConversationalRagChain.from_llm(
        rag_chain=get_rag_chain(),
        llm=get_llm_function(LLM_MODEL),
        callbacks=None
    )

# Route to get the document list
@local_app.route('/documents', methods=['GET'])
def list_documents():
    files = os.listdir(local_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"/files/{f}", "extension":os.path.splitext(f)[1][1:]} for f in files]
    return jsonify(documents)

# Route to get a single document
@local_app.route('/documents/<document_name>', methods=['GET'])
def get_document(document_name):
    files = os.listdir(local_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"/files/{f}", "extension": os.path.splitext(f)[1][1:]} for f in files]
    
    document = next((doc for doc in documents if doc["name"] == document_name), None)
    print(document)
    
    if document is None:
        return jsonify({'error': 'Document not found'}), 404
    
    return jsonify(document)

# Route to show the pdf
@local_app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(local_app.config['UPLOAD_FOLDER'], filename)


@local_app.route("/")
def index():
    return render_template('local.html')


@local_app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg","")
    input = msg
    return get_Chat_response(input)


def get_Chat_response(query):
    inputs = {
    "query": str(query),
    "chat_history": []
    }
    res = rag_conv._call(inputs)

    output = jsonify({
        'response': res['result'],
        'context': res['context'],
        'source': res['source']
    })
    return output


if __name__ == '__main__':
    init_app()
    local_app.run(port=5000,debug=True)