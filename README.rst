Image Cleaner
=============

Remove duplicated images from a path.


Installation
------------

You can install image cleaner using pip.

.. code-block:: console

   $ pip install imagecleaner
   # or install master branch
   $ pip install git+git@github.com:Kjwon15/image-cleaner.git


Usage
-----

It's just simple one command!

.. code-block:: console

   $ image-cleaner <path>


Reference
---------

http://blog.iconfinder.com/detecting-duplicate-images-using-python/


Change logs
-----------

0.4.0
~~~~~

- Fix logging.
- Adjustment threads count by command argument.

0.3.2
~~~~~

- Handle interrupt.
- Caching dhash to run faster.


0.3.1
~~~~~

- Improvement speed by using multi-thread.
- Change default hash size from 8 to 16.


0.3.0
~~~~~

- Added help message for simulate mode.
- Leave last modified image when they has same size.
- Image cleaner can remove images from multiple paths.


0.2.0
~~~~~

- Add simulate mode. It does not remove file.
- Enable logging when simulate mode.
- Handle malformed images.


License
-------

Image Cleaner is following MIT license.
