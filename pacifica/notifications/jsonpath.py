#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The jsonpath interface module."""
from jsonpath2.path import Path


def parse(jsonpath_str):
    """Parse the json path."""
    return Path.parse_str(jsonpath_str)


def find(expr, data):
    """Match the expression in the data and return truthy value."""
    return bool(list(expr.match(data)))
