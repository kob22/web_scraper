import pytest
from app.api.helpers import validate_url
import json


@validate_url
def return_url(url):
    return url


class TestURLS:

    def test_protocols(self, client):
        assert 'https://www.google.com/' == return_url('https://www.google.com/')
        assert 'http://www.google.pl/' == return_url('http://www.google.pl/')
        assert 'ftp://ftp.xyz.com' == return_url('ftp://ftp.xyz.com')
        urls = ['htt://www.google.com/', 'httpa://www.google.pl/]', 'ft://ftp.xyz.com']

        for url in urls:
            response = return_url(url)
            assert response.status == '400 BAD REQUEST'
            assert json.loads(response.data) == {"error": "URL is incorrect"}
            assert response.mimetype == 'application/json'
