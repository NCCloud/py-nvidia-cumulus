import requests


def url_safe(name: str):
    """
    Escape reserved characters in the object name
    """
    return requests.utils.quote(name, safe="")
