from functools import wraps

from flask import jsonify, request


def paginated_response(items_key, default_per_page=10):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            page = request.args.get("page", 1, type=int)
            per_page = request.args.get("per_page", default_per_page, type=int)

            result = f(*args, **kwargs)

            if isinstance(result, list):
                items = result
                response = {}
            elif isinstance(result, dict):
                items = result.get(items_key, [])
                response = {k: v for k, v in result.items() if k != items_key}
            else:
                return result

            total_items = len(items)
            total_pages = (total_items + per_page - 1) // per_page
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_items = items[start_idx:end_idx]

            response[items_key] = paginated_items
            response["pagination"] = {
                "current_page": page,
                "per_page": per_page,
                "total_items": total_items,
                "total_pages": total_pages,
            }

            return jsonify(response)

        return decorated_function

    return decorator
