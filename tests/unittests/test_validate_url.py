from unittest.mock import Mock
from app.api.helpers import validate_url


def test_validate_url_decorator_with_correct_url():

    func = Mock()
    decorated_func = validate_url(func)
    url = "https://www.google.pl/"
    decorated_func(url)

    assert func.called


def test_validate_url_decorator_with_incorret_url():

    func = Mock()
    decorated_func = validate_url(func)
    url = "google.pl"
    decorated_func(url)

    assert not func.called