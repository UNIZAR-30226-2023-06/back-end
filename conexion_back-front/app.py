# from flask import Flask, request, jsonify
# from flask_cors import CORS
from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

class Item(BaseModel):
    make: str
    model: str
#    model: Union[str, None] = None

# Creamos una instancia de la aplicación Flask.
# app = Flask(__name__)
app = FastAPI()
# app = FastAPI(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuramos Flask para que pueda manejar solicitudes de otros dominios.
# cors = CORS(app)

# Creamos una ruta para manejar solicitudes HTTP POST en la ruta "/receiver".
# Definimos una función llamada "postME" que manejará la solicitud.
# @app.route("/receiver", methods=["POST"])
# def postME():

    # Obtenemos los datos de la solicitud POST en formato json.
#     data = request.get_json()

    # Realizamos el tratamiento de los datos
#     for car in data:
#         car["model"] = car["model"] + " - funciona!!"

    # Convertimos los datos a json (redundante) y los devolvemos.
#     return jsonify(data)

# Creamos una ruta para manejar solicitudes HTTP POST en la ruta "/receiver".
# Definimos una función llamada "postME" que manejará la solicitud.
@app.post("/receiver/")
async def create_item(item: Item):
    # item.model = "funciona!!"
    return item


# Si estamos ejecutando este script directamente (no como un módulo importado),
# iniciamos el servidor web Flask.
# if __name__ == "__main__": 

    # Configuramos Flask para que ejecute en modo depuración.
#     app.run(debug=True)
