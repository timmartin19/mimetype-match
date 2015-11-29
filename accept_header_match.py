from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import fnmatch
import sys

import six


class InvalidMimeType(Exception):
    """
    An exception for invalid mimetypes. Valid mimetypes
    have the format of <type>/<specific>.  They must
    can have a wildcard in either place but their must be at
    least one forward slash
    """


def _is_more_specific(first, second):
    """
    Compares how specific two mimetypes are. Returns
    True if the first is more specific, False if the second
    is more specific and None if neither is more specific.

    :param str first: The first mimetype
    :param str second: The second mimetype to compare
    :raises IndexError: Raises an index error if there
        is not at least one forward slash as required by
        mimetypes.
    """
    first = first.split('/')
    second = second.split('/')
    if first[0] == '*' and not second[0] == '*':
        return False
    if not first[0] == '*' and second[0] == '*':
        return True
    if first[1] == '*' and not second[1] == '*':
        return False
    if not first[1] == '*' and second[1] == '*':
        return True
    return None


class MimeType(object):
    """
    A Mimetype object that is comparable.  All comparison operations
    (==, >, <, etc) are available.  The comparisions are to determine
    which mimetype should be picked.  It is ordered according to
    the `Http Specification <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html>`_.

    Additionally, it strips off the weight and makes that available
    independently and the actual mimetype as well.
    """

    def __init__(self, mimetype_string):
        """
        :param str mimetype_string: The mimetype string optionally,
            with the weight attached (e.g. "text/html;q=0.7").  Wildcard
            syntax are also valid.
        :raises InvalidMimeType: If the mimetype is not valid.
        """
        if not mimetype_string:
            raise InvalidMimeType('Invalid Mimetype')
        mimetype_string = mimetype_string.strip().strip(';')
        self._full = mimetype_string
        parts = [part.strip().strip(';') for part in mimetype_string.split(';')]
        parts = [part for part in parts if part]
        if not parts or len(parts[0].split('/')) < 2:
            raise InvalidMimeType('Invalid Mimetype')
        if len(parts) == 1 or not parts[-1].startswith('q='):
            self.mimetype = mimetype_string
            self.weight = 1.0
        else:
            try:
                self.mimetype = ';'.join(parts[:-1])
                weight = parts[-1][2:].strip()
                self.weight = float(weight)
            except ValueError:
                raise InvalidMimeType('{0} is not valid'.format(parts[-1]))

    def __eq__(self, other):
        """
        :param MimeType other: The MimeType to compare
        :return: A boolean indicating if the MimeType is equal
            equal in precidence
        :rtype: bool
        """
        if not other:
            return False
        if not self.weight == other.weight:
            return False
        specificity = _is_more_specific(self.mimetype, other.mimetype)
        return specificity is None

    def __gt__(self, other):
        """
        :param MimeType other: The MimeType to compare
        :return: A boolean indicating if the MimeType is greater than
            in precidence
        :rtype: bool
        """
        if not other:
            return True
        specificity = _is_more_specific(self.mimetype, other.mimetype)
        if specificity is not None:
            return specificity
        return self.weight > other.weight

    def __lt__(self, other):
        """
        :param MimeType other: The MimeType to compare
        :return: A boolean indicating if the MimeType is less than
            in precidence
        :rtype: bool
        """
        if not other:
            return False
        specificity = _is_more_specific(self.mimetype, other.mimetype)
        if specificity is not None:
            return not specificity
        return self.weight < other.weight

    def __ge__(self, other):
        """
        :param MimeType other: The MimeType to compare
        :return: A boolean indicating if the MimeType is greater than
            or equal in precidence
        :rtype: bool
        """
        if not other:
            return True
        specificity = _is_more_specific(self.mimetype, other.mimetype)
        if specificity is not None:
            return specificity
        return self.weight >= other.weight

    def __le__(self, other):
        """
        :param MimeType other: The MimeType to compare
        :return: A boolean indicating if the MimeType is less than
            or equal in precidence
        :rtype: bool
        """
        if not other:
            return False
        specificity = _is_more_specific(self.mimetype, other.mimetype)
        if specificity is not None:
            return not specificity
        return self.weight <= other.weight

    def is_match(self, string):
        """
        Returns true if the string matches the mimetype.
        Otherwise it returns False.

        :rtype: bool
        """
        return fnmatch.fnmatch(string, self.mimetype)


class AcceptHeader(object):
    """
    Parses an Accept header for the various mimetypes
    and sorts them in order of relevance.  It is iterable
    so it is entirely valid to simply call

    .. code-block:: python

        mimetypes = AcceptHeader(accept_header_str)
        for mimetype in mimetypes:
            # Do something

    They are ordered with the first being the preferred mimetype.
    All of the mimetypes are MimeType objects where the weight
    and actual mimetype string are available.
    """
    def __init__(self, accept_header):
        """
        :param str accept_header: The accept header with comma
            delimited mimetypes according to the
            `HTTP Specification <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html>`_
        """
        self.mimetypes = []
        for accept in accept_header.split(','):
            accept = accept.strip()
            if not accept:
                continue
            self.mimetypes.append(MimeType(accept))
        self.mimetypes.sort(reverse=True)

    def __iter__(self):
        for mimetype in self.mimetypes:
            yield mimetype

    def get_match(self, mimetype):
        """
        Check if a mimetype
        is one of the requested mimetypes
        according to the Accept Header.

        :param str mimetype: The mimetype to compare
            to the ones in the Accept header.
        :returns: A MimeType object that includes the
            weight and mimetype string
        :rtype: MimeType
        """
        for mime in self:
            if mime.is_match(mimetype):
                return mime
        return None

    def get_best_match(self, mimetype_list):
        """
        Finds the preferred mimetype of the client
        from the mimetype list.  If none of the types
        in the mimetype list match any of the mimetypes
        provided in the Accept header, then it returns None.

        :param list[str|unicode]|tuple(unicode|str) mimetype_list: A list
            of strings to compare and find the best match
        :returns: A tuple with the first item being the matched
            mimetype from the client and the second item a string
            mimetype that the server has available.
        :rtype: tuple(MimeType, str)
        """
        content_types = [(self.get_match(mimetype), mimetype) for mimetype in mimetype_list]
        best = max(content_types)
        if not best[0]:
            return None
        return best


def get_best_match(accept_header, served_types):
    """
    A shortcut to find the best mimetype from the available mimetypes
    in the accept header.

    :param str|unicode|list[str|unicode]|tuple(str|unicode) accept_header: A comma
        delimited string that corresponds
        to the `Accept Header <http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html>`_
        or an interable of strings mimetypes.
    :param list|tuple served_types: A list of mimetypes corresponding to
    :returns: The a tuple with the first object being the matched MimeType object
        and the string mimetype that the server accepts as the second.
    :rtype: tuple(MimeType, str)|NoneType
    """
    if not isinstance(accept_header, six.string_types):
        accept_header = ','.join(accept_header)
    return AcceptHeader(accept_header).get_best_match(served_types)


def cli():
    """
    A tool to find the best matched mimetype for a particular
    Accept header. The first argument should be the comma delimited
    mimetypes as an appropriately formatted accept header.
    The additional arguments are the mimetypes from the server
    that you wish to match. For example you may have an Accept header
    of the following:
    ``text/*;q=0.3, text/html;q=0.7, text/html;level=1, /html;level=2;q=0.4, */*;q=0.5``
    and the server can serve the following content types:
    ``["text/html", "application/json", "audio/basic"]``

    In this case we would run the following command:

    .. code-block:: bash

        mimetype-match "text/*;q=0.3, text/html;q=0.7, text/html;level=1, /html;level=2;q=0.4, */*;q=0.5" "text/html" "application/json" "audio/basic"

    This command would tell you that "text/html" is the best choice.
    """
    if not sys.argv or sys.argv[0] in ['--help', '-h']:
        print(cli.__doc__)
        return
    if len(sys.argv) < 2:
        print("======================================")
        print("At least two arguments are required")
        print("======================================")
        print(cli.__doc__)
    accept = sys.argv[0]
    matches = sys.argv[1:0]
    best = get_best_match(accept, matches)
    print("The best match is to {0} with the mimetype {1}".format(best[0].content_type, best[1]))
