from collections import namedtuple
import logging

from pyramid_secure_response import __name__ as PACKAGE_NAME


logger = logging.getLogger(PACKAGE_NAME)  # pylint: disable=invalid-name


def _get_config_value_f(registry, config_key=''):
    # type: (Registry, str) -> 'function'
    """Gets configured value from .ini file via registry."""
    if not config_key:
        raise ValueError

    s = registry.settings

    def _get_value_f(key, default):
        v = s.get('{:s}.{:s}'.format(config_key, key), default)
        if v == default:
            return v
        v = str(v)
        if v.lower() == 'true':
            return True
        elif v.lower() == 'false':
            return False
        if '\n' in v:
            return tuple(v.split())

        return v

    return _get_value_f


def _build_config(prefix='', defaults=tuple(), registry=None):
    # pylint: disable=invalid-name
    if prefix:
        config_key = '{:s}.{:s}'.format(PACKAGE_NAME, prefix)
    else:
        config_key = PACKAGE_NAME

    get_value_f = _get_config_value_f(registry, config_key=config_key)

    Config = namedtuple('Config', [k for k, _ in defaults])
    return Config(**dict([(k, get_value_f(k, v)) for k, v in defaults]))


def get_config(registry):  # type: (Registry) -> namedtuple
    """Returns namedtuple instance object has configuration."""
    # HTTP Redirections (ssl_redirect.xxx)
    ssl_redirect = _build_config(prefix='ssl_redirect', defaults=(
        ('enabled', True),
        ('proto_header', ''),
        ('ignore_paths', tuple()),
    ), registry=registry)

    # HTTP Strict Transport Security (hsts_support.xxx)
    hsts_support = _build_config(prefix='hsts_support', defaults=(
        ('enabled', True),
        ('proto_header', ''),
        ('ignore_paths', tuple()),
        ('max_age', '31536000'),  # seconds, 1 year
        ('include_subdomains', True),
        ('preload', True),
    ), registry=registry)

    # Content Security Policy (csp_coverage.xxx)
    csp_coverage = _build_config(prefix='csp_coverage', defaults=(
        ('enabled', True),
        ('ignore_paths', tuple()),

        # NOTE:
        #   These directives are appended into header as alphabetical
        #   order by directive sections.
        # [fetch]
        ('child_src', ''),  # (deprecated)
        ('connect_src', ''),
        ('default_src', ''),
        ('font_src', ''),
        ('frame_src', ''),
        ('img_src', ''),
        ('manifest_src', ''),
        ('media_src', ''),
        ('object_src', ''),
        ('script_src', ''),
        ('style_src', ''),
        ('worker_src', ''),
        # [document]
        ('base_uri', ''),
        ('plugin_types', ''),
        ('sandbox', ''),
        # [navigation]
        ('form_action', ''),
        ('frame_ancestors', ''),
        # [reporting]
        ('report_uri', ''),  # (deprecated)
        ('report_to', ''),
        # [other]
        ('block_all_mixed_content', False),
        ('referrer', ''),  # (obsolete)
        ('require_sri_for', ''),
        ('upgrade_insecure_requests', False),
    ), registry=registry)

    # Shared
    return _build_config(prefix='', defaults=(
        ('proto_header', ''),   # e.g. X-Forwarded-Proto
        ('ignore_paths', tuple()),

        ('ssl_redirect', ssl_redirect),
        ('hsts_support', hsts_support),
        ('csp_coverage', csp_coverage),
    ), registry=registry)


def apply_path_filter(req, paths):  # type: (Request, tuple) -> bool
    if paths:
        return any([req.path.startswith(path) for path in paths])
    return False


def build_criteria(req, **kwargs):  # type: (Request, dict) -> tuple
    """Builds criteria contains about incoming request.

    This function is used for following tweens:

    * ssl_redirect
    * hsts_support
    """
    criteria = [
        req.url.startswith('https://'),
    ]
    if 'proto_header' in kwargs:
        proto_header = kwargs.get('proto_header', None)
        if proto_header:
            criteria.append(req.headers.get(proto_header, 'http') == 'https')

    return tuple(criteria)
