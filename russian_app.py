import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_script'))

from parameters import load_api_keys,load_config
from flask import Flask, render_template, request, jsonify
from random import randint

DATA_PATH = None
CHROMA_ROOT_PATH = None
EMBEDDING_MODEL = None
LLM_MODEL = None
PROMPT_TEMPLATE = None

russian_app = Flask(__name__)

@russian_app.route("/")
def index():
    return render_template('russian_index.html')


@russian_app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg","")
    input = msg
    return get_Chat_response(input)


def get_Chat_response(text):
    response,context,source = query_rag(str(text))
    output = jsonify({
        'response': response,
        'context': context,
        'source': source
    })
    return output
    

if __name__ == '__main__':
    load_api_keys()
    load_config('russian')
    from query_data import query_rag
    russian_app.run(port=5000,debug=False)
