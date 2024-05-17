from flask import Flask, render_template, request, jsonify
from query_data import query_rag
from random import randint

app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')


@app.route("/get", methods=["POST"])
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
    app.run(debug=True)
