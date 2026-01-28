from config import init_db
from flask import Flask
from flask_cors import CORS
from routes.players_information import players_information_bp
from routes.rule import rule_bp

app = Flask(__name__)
CORS(app)

init_db(app)


app.register_blueprint(players_information_bp, url_prefix="/api/players_information")
app.register_blueprint(rule_bp, url_prefix="/api/rule")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
