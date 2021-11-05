import folium
from folium.plugins import HeatMap
from flask import Flask,request
from flask_cors import CORS
import json
import pandas as pd

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}} , support_credentials=True)

@app.route('/', methods=['POST'])
def getmap():
    req = json.loads(request.data)
    data = req['data']
    rainfall_df = pd.json_normalize(data)
    rainfall_df = rainfall_df[rainfall_df['Rainfall'] > -1]
    mapobj = folium.Map([19.0760, 72.8777], zoom_start=10)
    maximum = rainfall_df["Rainfall"].max()
    mapdata = rainfall_df[["Latitude","Longitude",'Rainfall']]
    mapdata["Rainfall"] = mapdata["Rainfall"]* 100 / maximum
    # optional step doesnt do anything ( Just in case Heatmap gives type error)
    # mapdata = mapdata.to_numpy()
    colorgradient = {0.0: 'blue', 0.6: 'cyan',   0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
    HeatMap(mapdata, gradient=colorgradient, radius=15).add_to(mapobj)
    return mapobj._repr_html_()

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5000, debug=True)

# Pythonanywhere
# if __name__ == "__main__":
#     app.run()

PRODUCTION
if __name__ == "__main__":
    from waitress import serve
    serve(app,host='0.0.0.0', port=5000)
