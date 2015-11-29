Accept-Header-Match
===================

.. image:: https://travis-ci.org/vertical-knowledge/ripozo.svg?branch=master&style=flat
    :target: https://travis-ci.org/vertical-knowledge/mimetype-match
    :alt: test status

.. image:: https://readthedocs.org/projects/ripozo/badge/?version=latest
    :target: https://mimetype-match.readthedocs.org/
    :alt: Documentation Status

A tool to make parsing Accept headers and finding the appropriate mimetype to
return easy.  Simply pass your accept header and the mimetype your server can
return and it will find the best match.

There is both a programmatic interface to this package as well as a
command line interface.

Installation
------------

It can easily be installed using pip

.. code-block:: bash

    pip install mimetype-match

Or if you prefer clone the repo and install it simply run the following
from the root directory of the package.

.. code-block:: bash

    python setup.py develop

Full Documentation
------------------

`Documentation <https://mimetype-match.readthedocs.org/>`_

Using the command line interface
--------------------------------

.. code-block:: bash

    mimetype-match [accept-header] [server-mimetype1] [server-mimetype2] ...

The first argument should be the comma delimited
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

Using the package
-----------------

Using the package programmatically is very similar to the cli.

.. code-block:: python

    from mimetype_match import AcceptHeader

    available_types = ["text/html", "application/json", "audio/basic"]
    accept_header = AcceptHeader("text/*;q=0.3, text/html;q=0.7, text/html;level=1, /html;level=2;q=0.4, */*;q=0.5")
    best_match = accept_header.get_best_match(available_types)
    # It returns a tuple.  The first object is a MimeType object
    # which has the orinal requested type from the client
    # The second object is the available type from the
    # server that best matches the clients requested types.
    print(best_match[0].mimetype)
    print(best_match[0].weight)
    print(best_match[1])


Versioning
----------

Prior to version 1.0.0 versioning follows `sentimental
versioning <http://sentimentalversioning.org/>`_.   Releases after 1.0.0 ollow
a standard *major.minor.patch* style.

- patch: forwards and backwards compatible
- minor: backwards compatible
- major: No guarantees

Contributing
------------

Want to help out? We'd love it! Github will be the hub of development for mimetype-matching.
If you have any issues, comments, or complaints post them there.  Additionally, we
are definitely accepting pull requests (hint: we almost always love more tests and
documentation).  We do have just a few requests:

* Every method, function, and class should have a thorough docstring
* There should be at least one unit test for each function and method
* Keep your pull requests to one issue. (Preferably open an issue on github first for record keeping)
