Freezing to cbz
################

``ftcbz`` is a command line tool for archive multiple comic books to ``.cbz`` format.

This tool can process both directories or ``.rar`` & ``.cbr`` files to ``.cbz`` and remove the password too. (rar relate function require ``unrar``)

Example
==============

Example folders structure
---------------------------

::

    ALLDIR - COMICDIR1 - VOLUME1
                       - VOLUME2
                       - VOLUME3
           - COMICDIR2 - VOLUME4
                       - VOLUME5

Each ``VOLUME`` could be a folder or a rar file.

When convert done, new structure look like.

::

    ALLDIR - COMICDIR1 - VOLUME1
                       - VOLUME1.cbz
                       - VOLUME2
                       - VOLUME2.cbz
                       - VOLUME3
                       - VOLUME3.cbz
           - COMICDIR2 - VOLUME4
                       - VOLUME4.cbz
                       - VOLUME5
                       - VOLUME5.cbz

It can also remove the original ``VOLUME`` automatic if you want.

command
---------

To convert above 5 "VOLUME" to ``.cbz``, using the following commands...

.. code:: bash

    ftcbz COMICDIR1 COMICDIR2

or

.. code:: bash

    ftcbz --all ALLDIR

Install
=============

Make sure your python >= 3.3, then...

.. code:: bash

    pip3 install ftcbz
