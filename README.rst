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


`pyramid_secure_response`_ handles request to provide secure response.

* redirects http as https
* sets HSTS Header to response
* sets CSP Header to response

For response headers (HSTS, CSP), the tweens do not set anything if that
already exist in your response. This means you can set these values by yourself
as you need (e.g. at view action)


Repository
----------

https://gitlab.com/grauwoelfchen/pyramid_secure_response


Install
-------

.. code:: zsh

    % pip install pyramid_secure_response


Features
--------

``pyramid_secure_response`` has 3 tweens:

* HTTP Redirecton (`ssl_redirect`_, +http+ request will be redirected as
  +https+ on same host)
* HSTS Support (`hsts_support`_, The ``HTTP Strict Transport Security`` will be
  set in response)
* CSP Coverage ( `csp_coverage`_, The ``Content Security Policy`` will be set
  in response)

With few additional features.

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

Code
~~~~

Or you can include in python code.

.. code:: python

    config.include('pyramid_secure_response')

It's also available to add tween(s) directly, as you need.

.. code:: python

    config.add_tween('pyramid_secure_response.ssl_redirect.tween')
    config.add_tween('pyramid_secure_response.hsts_support.tween')
    config.add_tween('pyramid_secure_response.csp_coverage.tween')

You may want to add also kwargs ``under`` or ``over``. (
See `pyramid.config.Configurator.add_tween`_.)

By default, *ssl_redirect* tween will be handled before another tweens.

.. code:: python

    config.add_tween('pyramid_secure_response.ssl_redirect.tween',
                     over=tweens.MAIN)
    config.add_tween('pyramid_secure_response.hsts_support.tween',
                     over=tweens.MAIN, under='pyramid_secure_response.ssl_redirect.tween')
    config.add_tween('pyramid_secure_response.csp_coverage.tween',
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

    pyramid_secure_response.csp_coverage.enabled = True
    pyramid_secure_response.csp_coverage.script_src = https://example.com
    pyramid_secure_response.csp_coverage.default_src = self

    # fallback (global)
    pyramid_secure_response.proto_header = X-Forwarded-Proto
    pyramid_secure_response.ignore_paths =
        /_ah/health
        /internal_api/xxx

Default values
**************

ssl_redirect
~~~~~~~~~~~~

+--------------+----------------+--------+-------------------------+
| Key          | Value (INI)    | Type   | Note                    |
+==============+================+========+=========================+
| enabled      | ``'True'``     | *bool* | Enable ``ssl_redirect`` |
|              |                |        | tween                   |
+--------------+----------------+--------+-------------------------+
| proto_header | ``''``         | *str*  | An header like          |
|              |                |        | *X-Forwarded-Proto*     |
|              |                |        | Checked in criteria as  |
|              |                |        | ``'https'`` if exists   |
+--------------+----------------+--------+-------------------------+
| ignore_paths | ``''``         | *list* | Splittable string like  |
|              |                |        | *\n/path\n/path\n*      |
|              |                |        | Skipped if matched      |
+--------------+----------------+--------+-------------------------+

hsts_support
~~~~~~~~~~~~

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
|                    |                |        | *X-Forwarded-Proto*     |
|                    |                |        | Checked in criteria as  |
|                    |                |        | ``'https'`` if exists   |
+--------------------+----------------+--------+-------------------------+
| ignore_paths       | ``''``         | *list* | Splittable string like  |
|                    |                |        | *\n/path\n/path\n*      |
|                    |                |        | Skipped if matched      |
+--------------------+----------------+--------+-------------------------+

csp_coverage
~~~~~~~~~~~~

+---------------------------+-------------+--------+----------------------------------+
| Key                       | Value (INI) | Type   | Note                             |
+===========================+=============+========+==================================+
| enabled                   | ``'True'``  | *bool* | Enable ``csp_coverage`` tween    |
+---------------------------+-------------+--------+----------------------------------+
| child_src                 | ``''``      | *str*  | ``child-src`` fetch directive    |
|                           |             |        | <source> (deprecated)            |
+---------------------------+-------------+--------+----------------------------------+
| connect_src               | ``''``      | *str*  | ``connect-src`` fetch directive  |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| default_src               | ``''``      | *str*  | ``default-src`` fetch directive  |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| font_src                  | ``''``      | *str*  | ``font-src`` fetch directive     |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| frame_src                 | ``''``      | *str*  | ``frame-src`` fetch directive    |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| img_src                   | ``''``      | *str*  | ``img-src`` fetch directive      |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| manifest_src              | ``''``      | *str*  | ``manifest-src`` fetch directive |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| media_src                 | ``''``      | *str*  | ``media-src`` fetch directive    |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| object_src                | ``''``      | *str*  | ``object-src`` fetch directive   |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| script_src                | ``''``      | *str*  | ``script-src`` fetch directive   |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| style_src                 | ``''``      | *str*  | ``style-src`` fetch directive    |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| worker_src                | ``''``      | *str*  | ``worker-src`` fetch directive   |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| base_uri                  | ``''``      | *str*  | ``base-uri`` document directive  |
|                           |             |        | <source>                         |
+---------------------------+-------------+--------+----------------------------------+
| plugin_types              | ``''``      | *str*  | ``plugin-types`` document        |
|                           |             |        | directive <type>/<subtype>       |
+---------------------------+-------------+--------+----------------------------------+
| sandbox                   | ``''``      | *str*  | ``sandbox`` document directive   |
|                           |             |        | <value>                          |
+---------------------------+-------------+--------+----------------------------------+
| form_action               | ``''``      | *str*  | ``form-action`` navigation       |
|                           |             |        | directive <source>               |
+---------------------------+-------------+--------+----------------------------------+
| frame_ancestors           | ``''``      | *str*  | ``frame-ancestors`` navigation   |
|                           |             |        | directive <source>               |
+---------------------------+-------------+--------+----------------------------------+
| report_uri                | ``''``      | *str*  | ``report_uri`` reporting         |
|                           |             |        | directive <uri>                  |
+---------------------------+-------------+--------+----------------------------------+
| report_to                 | ``''``      | *str*  | ``report_to`` reporting          |
|                           |             |        | directive <uri>                  |
+---------------------------+-------------+--------+----------------------------------+
| block_all_mixed_content   | ``'False'`` | *bool* | ``block_all_mixed_content``      |
|                           |             |        | directive value                  |
+---------------------------+-------------+--------+----------------------------------+
| referrer                  | ``''``      | *str*  | ``referrer`` directive value     |
|                           |             |        | such as ``"origin"`` (obsolete)  |
+---------------------------+-------------+--------+----------------------------------+
| require_sri_for           | ``''``      | *str*  | ``require_sri_for`` directive    |
|                           |             |        | value                            |
+---------------------------+-------------+--------+----------------------------------+
| upgrade_insecure_requests | ``'False'`` | *bool* | ``upgrade_insecure_requests``    |
|                           |             |        | directive value                  |
+---------------------------+-------------+--------+----------------------------------+
| ignore_paths              | ``''``      | *list* | Splittable string like           |
|                           |             |        | *\n/path\n/path\n*. Skipped, if  |
|                           |             |        | matched                          |
+---------------------------+-------------+--------+----------------------------------+

Note
****

Format
~~~~~~

For some policy values `<source>`, `<type>/<subtype>`, `<value>` and `<uri>`,
you don't need single quote for values. See above example section.

Syntax
~~~~~~

pyramid_secure_response moment does not validate value which is set by you, if
its syntax is valid or not, for now. Please check that yourself ;)

Fallback (global)
~~~~~~~~~~~~~~~~~

These values are like a global variables. If exist, its are also applied
to all tweens as fallback (If same keys are already exist for the tweens, it
will be taken priority, over these values).

+---------------+----------------+--------+-------------------------+
| Key           | Value (INI)    | Type   | Note                    |
+===============+================+========+=========================+
| proto_header  | ``''``         | *str*  | An header like          |
|               |                |        | *X-Forwarded-Proto*     |
|               |                |        | Checked in criteria as  |
|               |                |        | ``'https'`` if exists   |
+---------------+----------------+--------+-------------------------+
| ignore_paths  | ``''``         | *list* | Splittable string like  |
|               |                |        | *\n/path\n/path\n*      |
|               |                |        | Skipped if matched      |
+---------------+----------------+--------+-------------------------+

Links
~~~~~

- https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
- https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP



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
