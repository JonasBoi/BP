from flask import Flask
# from .QA_responder import qaResponder

# app init
app = Flask(__name__)

# qa system init
app.logger.info("Backend initialization.")
# qa_responder = qaResponder()

from . import requests
