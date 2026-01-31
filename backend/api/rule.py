from flask import Blueprint, jsonify

rule_bp = Blueprint("rule", __name__)

SALARY_CAP = 187895000


@rule_bp.route("/salary_cap", methods=["GET"])
def get_salary_cap():
    try:
        return jsonify({"salary_cap": SALARY_CAP})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
