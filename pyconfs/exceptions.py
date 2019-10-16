"""Exceptions for the PyConfs package

Custom exceptions used by PyConfs for more helpful error messages
"""


class PyConfsException(Exception):
    """Base class for all PyConfs exceptions"""


class ConversionError(PyConfsException):
    """Conversion of Configuration entries failed"""


class EntryError(PyConfsException):
    """Something is wrong with a given entry"""


class UnknownFormat(PyConfsException):
    """PyConfs does not know the given format"""
