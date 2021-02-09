import os
from flask import Flask
from flask_cors import CORS
from app_routes.slave_routes import slave_routes

app = Flask(__name__)
CORS(app)

app.register_blueprint(slave_routes)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port='8080'
    )
