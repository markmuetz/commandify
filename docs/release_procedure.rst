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
* Build/upload docs:
  * `cd docs`
  * `make html`
  * `make zip_html`
  * (Follow instructions to upload to PyPI)
* Update PyPI project:
  * `python setup.py sdist upload`
* git commit and tag release:
  * `git commit -a`
  * `git tag release_0.0.2`
  * `git push --tags`
