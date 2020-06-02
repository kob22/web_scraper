from functools import wraps
from validators.url import url as val_url
from flask import jsonify
from flask import make_response


def validate_url(func):
    """Decorator, validates urls"""
    @wraps(func)
    def decorated_function(url):
        if val_url(url) is not True:
            # todo return code error
            return make_response(jsonify({"error": "URL is incorrect"}), 400)
        return func(url)
    return decorated_function
