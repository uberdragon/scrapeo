"""Exceptions defined by the Scrapeo module"""


class ElementAttributeError(Exception):
    """Raised when an element does not have a specified attribute.

    Args:
        element (obj): the queried element
        attr (str): the missing attribute of the queried element
        message (str): explanation of error
    """
    def __init__(self, element, attr, message):
        self.element = element
        self.attr = attr
        self.message = message


class ElementNotFoundError(Exception):
    """Raised when an element is not found in the DOM.

    Args:
        message (str): explanation of error

    Keyword Args:
        search_term (str): name of element searched for
        attrs (dict): element attr-val pairs used in search
        value (str): single value used in search
    """
    def __init__(self, message, search_term='', attrs=None, value=''):
        self.search_term = search_term
        self.attrs = attrs
        self.value = value
        self.message = message
