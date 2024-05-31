import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.append(os.path.join(os.path.dirname(__file__), 'python_script'))
from parameters import load_config

###################
### LOAD CONFIG ###
###################
load_config('arch_ru')
from parameters import CHROMA_ROOT_PATH, EMBEDDING_MODEL, LLM_MODEL, PROMPT_TEMPLATE, DATA_PATH
from get_llm_function import get_llm_function
from get_rag_chain import get_rag_chain
from ConversationalRagChain import ConversationalRagChain

rag_conv = ConversationalRagChain.from_llm(
    rag_chain=get_rag_chain(),
    llm=get_llm_function(LLM_MODEL),
    callbacks=None
)
arch_ru_app = Flask(__name__)

arch_ru_app.config['UPLOAD_FOLDER'] = DATA_PATH

# Route to get the document list
@arch_ru_app.route('/documents', methods=['GET'])
def list_documents():
    files = os.listdir(arch_ru_app.config['UPLOAD_FOLDER'])
    documents = [{"name": f, "url": f"/arch-ru/files/{f}", "extension":os.path.splitext(f)[1][1:]} for f in files]
    return jsonify(documents)

# Route to show the pdf
@arch_ru_app.route('/files/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(arch_ru_app.config['UPLOAD_FOLDER'], filename)

@arch_ru_app.route("/")
def index():
    return render_template('arch_ru_index.html')


@arch_ru_app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg","")
    input_query = msg
    return get_Chat_response(input_query)


def get_Chat_response(query):
    inputs = {"query": str(query)}
    res = rag_conv._call(inputs)

    output = jsonify({
        'response': res['result'],
        'context': res['context'],
        'source': res['source']
    })
    return output
    
if __name__ == '__main__':
    arch_ru_app.run(port=6667,debug=False)
