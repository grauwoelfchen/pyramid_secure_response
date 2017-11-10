Pyramid Secure Response
=======================

.. image:: https://gitlab.com/grauwoelfchen/pyramid_secure_response/badges/master/pipeline.svg
        :target: https://gitlab.com/grauwoelfchen/pyramid_secure_response/commits/master
        :alt: Pipeline Status

.. image:: https://gitlab.com/grauwoelfchen/pyramid_secure_response/badges/master/coverage.svg
        :target: https://gitlab.com/grauwoelfchen/pyramid_secure_response/commits/master
        :alt: Coverage Report

.. image:: https://img.shields.io/pypi/v/pyramid_secure_response.svg
        :target: https://pypi.python.org/pypi/pyramid_secure_response/
        :alt: Version


`pyramid_secure_response`_ handles insecure request to provide secure response
(sets HSTS Header to https, redirects http as https).

Repository
----------

https://gitlab.com/grauwoelfchen/pyramid_secure_response


Install
-------

.. code:: zsh

    % pip install pyramid_secure_response


Features
--------

``pyramid_secure_response`` has 2 tweens.

* SSL Redirect (+http+ request will be redirected as +https+ on same host)
* HSTS Support (The ``HTTP Strict Transport Security`` will be set to https)

And an additional feature.

* Ignore path filter (matched paths with ``str.startswith()`` will be ignored)


Usage
-----

Setup
*****

INI file
~~~~~~~~

like `PasteDeploy`_ config file.

.. code:: INI

    pyramid.includes =
        pyramid_secure_response

Python
~~~~~~

Or you can include in python code.

.. code:: python

    config.include('pyramid_secure_response')

It's also available to add tween(s) directly, as you need.

.. code:: python

    config.add_tween('pyramid_secure_response.ssl_redirect.tween')
    config.add_tween('pyramid_secure_response.hsts_support.tween')

You may want to add also kwargs ``under`` or ``over``. (
See `pyramid.config.Configurator.add_tween`_.)

By default, *ssl_redirect* tween will be handled before *hsts_support*.

.. code:: python

    config.add_tween('pyramid_secure_response.ssl_redirect.tween',
                     over=tweens.MAIN)
    config.add_tween('pyramid_secure_response.hsts_support.tween',
                     over=tweens.MAIN, under='pyramid_secure_response.ssl_redirect.tween')

Configuration
*************

For example:

.. code:: INI

    pyramid_secure_response.ssl_redirect = False

    pyramid_secure_response.hsts_support = True
    pyramid_secure_response.hsts_max_age = 63072000
    pyramid_secure_response.hsts_include_subdomains = True
    pyramid_secure_response.hsts_preload = True

    pyramid_secure_response.proto_header = X-Forwarded-Proto
    pyramid_secure_response.ignore_paths =
        /_ah/health
        /internal_api/xx


Default values
**************

+-------------------------+----------------+--------+-------------------------+
| Key                     | Value (INI)    | Type   | Note                    |
+=========================+================+========+=========================+
| ssl_redirect            | ``'True'``     | *bool* | Enable ``ssl_redirect`` |
|                         |                |        | tween                   |
+-------------------------+----------------+--------+-------------------------+
| hsts_support            | ``'True'``     | *bool* | Enable ``hsts_support`` |
|                         |                |        | tween                   |
+-------------------------+----------------+--------+-------------------------+
| hsts_max_age            | ``'31536000'`` | *str*  | Add *max-age=N* into    |
|                         |                |        | HSTS Header (seconds)   |
+-------------------------+----------------+--------+-------------------------+
| hsts_include_subdomains | ``'True'``     | *bool* | Add *includeSubdomains* |
|                         |                |        | into HSTS Header        |
+-------------------------+----------------+--------+-------------------------+
| hsts_preload            | ``'True'``     | *bool* | Add *preload* into      |
|                         |                |        | HSTS Header             |
+-------------------------+----------------+--------+-------------------------+
| proto_header            | ``''``         | *str*  | An header like          |
|                         |                |        | *X-Forwarded-Proto*.    |
|                         |                |        | Checked in criteria as  |
|                         |                |        | ``'https'``, if exists. |
+-------------------------+----------------+--------+-------------------------+
| ignore_paths            | ``''``         | *list* | Splittable string like  |
|                         |                |        | *\n/path\n/path\n*.     |
|                         |                |        | Skiped, if matched.     |
+-------------------------+----------------+--------+-------------------------+



Development
-----------

See ``Makefile``.

.. code:: zsh

    (venv) % make check
    (venv) % make lint

    (venv) % make test
    (venv) % make coverage


License
-------

BSD 3-Clause "New" or "Revised" License (``BSD-3-Clause``)

See `LICENSE`_


.. _`pyramid_secure_response`: https://pypi.python.org/pypi/pyramid-secure-response
.. _`PasteDeploy`: https://docs.pylonsproject.org/projects/pyramid/en/latest/narr/paste.html
.. _`pyramid.config.Configurator.add_tween`: https://docs.pylonsproject.org/projects/pyramid/en/latest/api/config.html#pyramid.config.Configurator.add_tween
.. _`LICENSE`: LICENSE
