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


`pyramid_secure_response`_ handles insecure request to provide secure response.

* redirects http as https
* sets HSTS Header to response

For response headers (hsts), the tweens do not set anything if that
already exist in your response. This means you can set by yourself as you need
(e.g. at view action)


Repository
----------

https://gitlab.com/grauwoelfchen/pyramid_secure_response


Install
-------

.. code:: zsh

    % pip install pyramid_secure_response


Features
--------

``pyramid_secure_response`` has 2 tweens:

* HTTP Redirecton (`ssl_redirect`_, +http+ request will be redirected as
  +https+ on same host)
* HSTS Support (`hsts_support`_, The ``HTTP Strict Transport Security`` will be
  set in response)

With an additional feature.

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

By default, *ssl_redirect* tween will be handled before another tweens.

.. code:: python

    config.add_tween('pyramid_secure_response.ssl_redirect.tween',
                     over=tweens.MAIN)
    config.add_tween('pyramid_secure_response.hsts_support.tween',
                     over=tweens.MAIN, under='pyramid_secure_response.ssl_redirect.tween')

Configuration
*************

For example:

.. code:: INI

    pyramid_secure_response.ssl_redirect.enabled = False

    pyramid_secure_response.hsts_support.enabled = True
    pyramid_secure_response.hsts_support.max_age = 63072000
    pyramid_secure_response.hsts_support.include_subdomains = True
    pyramid_secure_response.hsts_support.preload = True

    # fallback (global)
    pyramid_secure_response.proto_header = X-Forwarded-Proto
    pyramid_secure_response.ignore_paths =
        /_ah/health
        /internal_api/xxx

Default values
**************

(ssl_redirect)

+--------------+----------------+--------+-------------------------+
| Key          | Value (INI)    | Type   | Note                    |
+==============+================+========+=========================+
| enabled      | ``'True'``     | *bool* | Enable ``ssl_redirect`` |
|              |                |        | tween                   |
+--------------+----------------+--------+-------------------------+
| proto_header | ``''``         | *str*  | An header like          |
|              |                |        | *X-Forwarded-Proto*.    |
|              |                |        | Checked in criteria as  |
|              |                |        | ``'https'``, if exists. |
+--------------+----------------+--------+-------------------------+
| ignore_paths | ``''``         | *list* | Splittable string like  |
|              |                |        | *\n/path\n/path\n*.     |
|              |                |        | Skiped, if matched.     |
+--------------+----------------+--------+-------------------------+

(hsts_support)

+--------------------+----------------+--------+-------------------------+
| Key                | Value (INI)    | Type   | Note                    |
+====================+================+========+=========================+
| enabled            | ``'True'``     | *bool* | Enable ``hsts_support`` |
|                    |                |        | tween                   |
+--------------------+----------------+--------+-------------------------+
| max_age            | ``'31536000'`` | *str*  | Add *max-age=N* into    |
|                    |                |        | HSTS Header (seconds)   |
+--------------------+----------------+--------+-------------------------+
| include_subdomains | ``'True'``     | *bool* | Add *includeSubdomains* |
|                    |                |        | into HSTS Header        |
+--------------------+----------------+--------+-------------------------+
| preload            | ``'True'``     | *bool* | Add *preload* into      |
|                    |                |        | HSTS Header             |
+--------------------+----------------+--------+-------------------------+
| proto_header       | ``''``         | *str*  | An header like          |
|                    |                |        | *X-Forwarded-Proto*.    |
|                    |                |        | Checked in criteria as  |
|                    |                |        | ``'https'``, if exists. |
+--------------------+----------------+--------+-------------------------+
| ignore_paths       | ``''``         | *list* | Splittable string like  |
|                    |                |        | *\n/path\n/path\n*.     |
|                    |                |        | Skiped, if matched.     |
+--------------------+----------------+--------+-------------------------+

These values are like a global variables. If exist, its are also applied
to all tweens as fallback (If same keys are already exist for the tweens, it
will be taken priority, over these values).

+---------------+----------------+--------+-------------------------+
| Key           | Value (INI)    | Type   | Note                    |
+===============+================+========+=========================+
| proto_header  | ``''``         | *str*  | An header like          |
|               |                |        | *X-Forwarded-Proto*.    |
|               |                |        | Checked in criteria as  |
|               |                |        | ``'https'``, if exists. |
+---------------+----------------+--------+-------------------------+
| ignore_paths  | ``''``         | *list* | Splittable string like  |
|               |                |        | *\n/path\n/path\n*.     |
|               |                |        | Skiped, if matched.     |
+---------------+----------------+--------+-------------------------+



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
