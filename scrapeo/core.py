"""Core Classes for the Scrapeo Package
=====================================

This module contains classes used to parse and handle HTML as a Python
object, search by combinations of element attribute and value pairs,
and scrape node and attribute value text from nodes.
"""

from bs4 import BeautifulSoup

import scrapeo.exceptions as exceptions
from .helpers import pop_kwargs

class Scrapeo(object):
    """Parse HTML into an object, search and get relevant element text.

    Facilitates searching and scraping functionality for appropriately
    parsed HTML.

    Args:
        html (str): string, HTML in text format

    Keyword Args:
        dom_parser (obj): an object that responds to the find message
        analyzer (obj): an object that responds to the relevant_text
            message
    """
    def __init__(self, html, dom_parser=None, analyzer=None):
        self.dom_parser = dom_parser or self.__default_dom_parser()(html)
        self.analyzer = analyzer or ElementAnalyzer()

    ### Public ###
    def get_text(self, search_term, **kwargs):
        """Search the dom tags and retrieve text from the results.

        .. todo:: Currently this encapsulates functionality to both search and
            scrape from parsed HTML, but the two bits of functionality
            should probably be separated into two public methods.

        Args:
            search_term (str): abritrary term to search the dom for,
                typically an element name

        Keyword Args:
            search_val (str): search for a tag containing this value
            seo_attr (str): specify which attribute to scrape a value from
            **kwargs: arbitrary number of attr-val pairs to search by

        Returns:
            str: The text from an element, which is either the node
                text or an attribute's value.
        """
        search_val, seo_attr = pop_kwargs(kwargs, 'search_val',
                                          'seo_attr')
        # search the dom for the provided keyword
        element = self.__dom_search(search_term, search_val=search_val,
                                    **kwargs)
        return self.__relevant_text(element, seo_attr=seo_attr)

    ### Private ###
    def __dom_search(self, search_term, **kwargs):
        return self.dom_parser.find(search_term, **kwargs)

    def __relevant_text(self, node, seo_attr=None):
        return self.analyzer.relevant_text(node, seo_attr=seo_attr)

    def __default_dom_parser(self):
        return DomNavigator


class DomNavigator(object):
    """Navigate HTML by searching for names, attributes, and values.

    Parses HTML in text format into an object suitable for searching.
    Provides a method to search the parsed HTML for an element name,
    an attribute-value pair, or simply by a value held by an arbirary
    attribute.

    .. todo:: DomNavigator should become WebScraper, and we're going to pass
        a URL to Scrapeo instead of HTML as a string. The WebScraper will
        do the work of making an HTTP request and retrieving the document.

    Args:
        html (str): any portion of HTML text

    Keyword Args:
        parser (obj): the object used to do the parsing
        parser_type (str): the type of python parser used by the parser
            object
    """
    def __init__(self, html, parser=None, parser_type='html5lib'):
        self.parser = parser or self.__default_parser()
        self.dom = self.__parse(html, parser_type)

    ### Public ###
    def find(self, search_term, search_val=None, **kwargs):
        """Find and return an HTML element using provided search terms.

        Args:
            search_term (str): search for elements by name

        Keyword Args:
            search_val (str): search for an element with an attribute
                value matching search_val
            **kwargs: arbitrary element attr-val pairs

        Returns:
            obj: HTML element as a python object

        Raises:
            ElementNotFoundError: When no element can be found using
                the search terms
        """
        ele_attrs = kwargs
        return self.__search_for(search_term, search_val, **ele_attrs)

    ### Private ###
    def __search_for(self, keyword, search_val, **kwargs):
        if search_val and not any(kwargs):
            tag = self.__search_by_value(keyword, search_val)
        else:
            tag = self.__search(keyword, **kwargs)

        if tag is None:
            exceptions.raise_element_not_found_error(search_term=keyword,
                                                     value=search_val,
                                                     attrs=kwargs)
            return
        return tag

    def __search(self, keyword, **kwargs):
        return self.dom.find(keyword, attrs=kwargs)

    def __search_by_value(self, keyword, value):
        for tag in self.dom.find_all(keyword):
            if value in tag.attrs.values():
                return tag

    def __parse(self, html, parser_type):
        return self.parser(html, parser_type)

    def __default_parser(self):
        return BeautifulSoup


class ElementAnalyzer(object):
    """Get text from an HTML element.

    Determines what useful or relevant text an HTML element contains
    and returns it as a string.
    """
    def __init__(self):
        pass

    ### Public ###
    def relevant_text(self, element, seo_attr=None):
        """Get pertinent text from an HTML element.

        Given an element's type and (optionally) a particular attribute,
        retrieve text from the element. Text could either be the text
        content of the node or the value of a particular attribute.

        Args:
            element (obj): object representing an HTML element which
                should implement the attributes is_empty_element and
                text, and support a dict-like get method for accessing
                attributes

        Keyword Args:
            seo_attr (str): attribute of element to retrieve a value
                from

        Returns:
            str: node text if the element is empty / self-closing or
                if seo_attr is not None, element attribute value as text
                otherwise

        Raises:
            ElementAttributeError: If seo_attr is not an attribute of
                element
        """
        if self.__is_empty_element(element) or seo_attr is not None:
            return self.__value_from_attr(element, seo_attr)
        return self.__node_text(element)

    ### Private ###
    def __value_from_attr(self, element, seo_attr):
        attr = 'content'
        if seo_attr is not None:
            # Overwrite the value of the relevant attribute
            attr = seo_attr
        val = element.get(attr)

        if val is None:
            exceptions.raise_element_attribute_error(element=element,
                                                     attr=attr)
        else:
            return val

    def __node_text(self, element):
        return element.text

    def __is_empty_element(self, element):
        return element.is_empty_element
