Release Procedure
=================

Before first release:

* [Check credentials in ``~/.pypirc``]
* ``python setup.py register``

For each release:

* Run tests:
    * ``python setup.py test``
    * [or ``nosetests``]
* Update ``commandify/version.py``
* Update ``changelog.rst``
* [If ``commandify_examples.py`` has changed:] update ``README.rst``
* Build/upload docs:
    * ``cd docs && make zip_html``
    * (Follow instructions to upload to PyPI)
* Update PyPI project:
    * ``python setup.py sdist upload``
* git commit and tag release:
    * ``git commit -a``
    * ``git push``
    * ``git tag release_0.0.2``
    * ``git push --tags``
