Change Log
==========

Version 0.0.4.5 (Alpha) - May 17, 2015
--------------------------------------

* Add support for ``argcomplete``

Version 0.0.4.3 (Alpha) - May 15, 2015
--------------------------------------

* Add in unit tests for main command only
* Change handling of ``parse_args`` in main parser so that the NS returned 
  has had e.g. ``not_some_arg=True`` replaced by ``some_arg=False``

Version 0.0.4.2 (Alpha) - May 15, 2015
--------------------------------------

* Fix serious bug that meant that all local vars in func were counted as arguments
* Auto setting of type=<type> for default args based on default's type
* Handle some_arg=[True|False] in natural way

Version 0.0.4.1 (Alpha) - May 14, 2015
--------------------------------------

* Change ``VERSION.txt`` to ``commandify/version.py``
* Allow for providing arguments for all functions
* Update setup.py to be able to run tests

Version 0.0.3.1 (Alpha) - May 13, 2015
--------------------------------------

* Switch to subclassing ``argparse.ArgumentParser`` to allow more flexibility.
* Allow for providing arguments for all functions

Version 0.0.2.2 (Alpha) - May 13, 2015
--------------------------------------

* Initial Python3 support
* Added example command (in docstrings) test
* Fixed some bad example commands
* Added a release procedure
* Allowed ``_commands`` and ``_main_command`` to be accessed though module

Version 0.0.1 (Alpha) - May 12, 2015
------------------------------------

* Basic functionality in place
    * Decorators for functions converted to command line args
    * Adding options to decorators
* Python project started
* Uploaded to PyPI

