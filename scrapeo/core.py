#!/usr/bin/env python

import re
from bs4 import BeautifulSoup

class Scrapeo(object):

    def __init__(self, html, dom_parser=None, analyzer=None):
        self.dom_parser = dom_parser or self.__default_dom_parser()(html)
        self.analyzer = analyzer or TextAnalyzer()

    """Public"""
    def get_text(self, search_term, seo_attr=None, **kwargs):
        """ Search the dom and retrieve some portion of text from one or more of the results

        search_term -- abritrary term to search the dom for, typically an element name
        keyword arguments:
        seo_attr -- specify the element's attribute to scrape the value from

        Additional keyword arguments may be any number of HTML element
        attribute=value pairs used to locate a particular tag
        """

        # search the dom for the provided keyword
        element = self.__dom_search(search_term, search_attr=seo_attr,
                                    **kwargs)
        return self.__relevant_text(element, seo_attr)

    """Private"""
    def __dom_search(self, search_term, **kwargs):
        return self.dom_parser.find(search_term, **kwargs)

    def __relevant_text(self, node, seo_attr):
        return self.analyzer.relevant_text(node, seo_attr=seo_attr)

    def __default_dom_parser(self):
        return DomNavigator


class DomNavigator(object):

    def __init__(self, html, parser=None, parser_type='html.parser'):
        self.parser = parser or self.__default_parser()
        self.dom = self.__parse(html, parser_type)

    """Public"""
    def find(self, search_term, search_attr=None, **kwargs):
        ele_attrs = kwargs
        return self.__search_for(search_term, search_attr, **ele_attrs)

    """Private"""
    def __search_for(self, keyword, search_attr, **kwargs):
        if search_attr and not any(kwargs):
            # assume the tag contains only one attribute, which is the one we're interested in
            kwargs[search_attr] = re.compile('.*')
        return self.dom.find(keyword, attrs=kwargs)

    def __parse(self, html, parser_type):
        return self.parser(html, parser_type)

    def __default_parser(self):
        return BeautifulSoup


class TextAnalyzer(object):

    def __init__(self):
        pass

    """Public"""
    def relevant_text(self, element, seo_attr=None):
        return self.__determine_text(element, seo_attr)

    """Private"""
    def __determine_text(self, element, seo_attr):
        if self.__is_empty_element(element):
            return self.__value_from_attr(element, seo_attr)
        return self.__node_text(element)

    def __node_text(self, element):
        return element.text

    def __value_from_attr(self, element, seo_attr):
        if seo_attr:
            # Return the text value of the relevant attribute
            return element[seo_attr]
        else:
            # Default is for the meta tag content attribute
            return element['content']

    def __is_empty_element(self, element):
        return element.is_empty_element
