from flask import Flask
from .QA_responder import qa_Responder

# app init
app = Flask(__name__)

# qa system init
app.logger.info("Backend initialization.")
qa_responder = qa_Responder()

from . import routes
