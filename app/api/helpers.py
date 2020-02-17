from validators.url import url as val_url
from functools import wraps
from flask import jsonify
from flask import make_response


def validate_url(f):
    """Decorator, validates urls"""
    @wraps(f)
    def decorated_function(url):
        if val_url(url) is not True:
            # todo return code error
            return make_response(jsonify({"error": "URL is incorrect"}), 400)
        return f(url)
    return decorated_function
