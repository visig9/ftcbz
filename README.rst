Folder to cbz
################

This is a command line tool to archive multiple comic books "volume dir" to ``.cbz`` format.

Example
==============

Example folder structure
---------------------------

::

    folder - comic_book_dir1 - vol_dir1
                             - vol_dir2
                             - vol_dir3
           - comic_book_dir2 - vol_dir1
                             - vol_dir2

command
---------

To convert above 5 "vol_dir" to cbz, using the following commands...

.. code:: bash

    ftcbz comic_book_dir1 comic_book_dir2

or

.. code:: bash

    ftcbz --all folder

Install
=============

Using ``python3-pip``\ , for example:

.. code:: bash

    python3-pip install ftcbz
