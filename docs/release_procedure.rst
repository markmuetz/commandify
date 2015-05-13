Release Procedure
=================

Before first release::

* [Check credentials in `~/.pypirc`]
* `python setup.py register`

For each release:

* Run tests:
  * `cd tests`
  * `nosetests`
* Update VERSION.txt
* Update PyPI project:
  * `python setup.py sdist upload`
* Build/upload docs:
  * `cd docs`
  * `make html`
  * `make zip_html`
  * (Follow instructions to upload to PyPI)
* Update ``changelog.rst``
* git commit and tag release:
  * `git commit -a`
  * `git tag release_0.0.2`
  * `git push --tags`
