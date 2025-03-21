import re


def is_valid_url(url):
    regex = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"

    pattern = re.compile(regex)

    return re.match(pattern, url)
