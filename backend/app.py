from api.auth import auth_bp
from api.basic_information import basic_information_bp
from api.lineup import lineup_bp
from api.rule import rule_bp
from api.stats import stats_bp
from config import get_current_config, init_db
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)

config = get_current_config()
frontend_domains = config.get("frontend_domains", [])

if frontend_domains:
    CORS(app, origins=frontend_domains, supports_credentials=True)
else:
    CORS(app)

init_db(app)


app.register_blueprint(basic_information_bp, url_prefix="/api/basic_information")
app.register_blueprint(stats_bp, url_prefix="/api/stats")
app.register_blueprint(rule_bp, url_prefix="/api/rule")
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(lineup_bp, url_prefix="/api/lineup")


if __name__ == "__main__":
    config = get_current_config()
    app.run(debug=config["env"] == "dev", port=5000, host="0.0.0.0")
