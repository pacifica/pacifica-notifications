#!/usr/bin/python
# -*- coding: utf-8 -*-
"""The jsonpath interface module."""
from six import PY2
# pylint: disable=import-error
if PY2:  # pragma: no cover only python 2
    from jsonpath_ng.ext import parse as jsonpath_parse
else:  # pragma: no cover only python 3
    from jsonpath2.path import Path
# pylint: enable=import-error

if PY2:  # pragma: no cover only python 2
    def parse(jsonpath_str):
        """Parse the jsonpath."""
        return jsonpath_parse(jsonpath_str)

    def find(expr, data):
        """Find the expression in the data."""
        return expr.find(data)
else:  # pragma: no cover only python 3
    def parse(jsonpath_str):
        """Parse the json path."""
        return Path.parse_str(jsonpath_str)

    def find(expr, data):
        """Match the expression in the data."""
        return expr.match(data)
