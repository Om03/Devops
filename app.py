import folium
from folium.plugins import HeatMap
from flask import Flask,request
from flask_cors import CORS
import json
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}} , support_credentials=True)

@app.route('/', methods=['GET'])
def getmap():
    return "Hello World"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# Pythonanywhere
# if __name__ == "__main__":
#     app.run()

# PRODUCTION
# if __name__ == "__main__":
#     from waitress import serve
#     serve(app,host='0.0.0.0', port=5000)
