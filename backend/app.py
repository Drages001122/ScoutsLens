from config import init_db
from flask import Flask
from flask_cors import CORS
from routes.players_information import players_information_bp

app = Flask(__name__)
CORS(app)

init_db(app)


app.register_blueprint(players_information_bp)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
