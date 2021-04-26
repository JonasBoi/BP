from .app import app, qa_responder
from flask import request, jsonify
from .api.jsonschema import (CONFIGURATION_JSON_SCHEMA,
                             PREDEFINED_QUESTIONS,
                             REQUEST_JSON_SCHEMA,
                             RESPONSE_JSON_SCHEMA,
                             SUPPORTED_MODELS_DICTIONARY)


@app.route('/json-schema', methods=['GET'])
def get_json_schema():
    schema = request.args.get('schema')

    if schema == "configuration":
        return jsonify(CONFIGURATION_JSON_SCHEMA)
    elif schema == "query-request":
        return jsonify(REQUEST_JSON_SCHEMA)
    if schema == "query-response":
        return jsonify(RESPONSE_JSON_SCHEMA)
    else:
        return f"Unknown schema '{schema}'.", 400


@app.route('/predefined-questions', methods=['GET'])
def get_question_list():
    return jsonify(PREDEFINED_QUESTIONS)


@app.route('/supported-models', methods=['GET'])
def supported_models():
    module = request.args.get('module')

    support = SUPPORTED_MODELS_DICTIONARY

    if module is None:
        return jsonify(support)

    if module in support:
        return jsonify(support[module])

    return f"Unsupported module '{module}'.", 400


@app.route('/query', methods=['POST'])
def query():
    r = request.get_json()
    question = r["question"][:200]

    predictions = qa_responder.find_answer(question, r["configuration"])

    return jsonify(predictions)
