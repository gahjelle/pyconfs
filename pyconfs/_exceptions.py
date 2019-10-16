"""Exceptions for the PyConfs package

Custom exceptions used by PyConfs for more helpful error messages
"""


class PyConfsException(Exception):
    """Base class for all PyConfs exceptions"""


class UnknownFormat(PyConfsException):
    """PyConfs does not know the given format"""
