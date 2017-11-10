from collections import namedtuple
import logging

from pyramid_secure_response import __name__ as PACKAGE_NAME


logger = logging.getLogger(PACKAGE_NAME)  # pylint: disable=invalid-name


def get_config_value_fn(registry, config_key=PACKAGE_NAME):
    # type: (Registry, str) -> 'function'
    """Gets configured value from .ini file via registry."""
    if not config_key:
        raise ValueError

    s = registry.settings

    def _get_value(key, default):
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

    return _get_value


def get_config(registry):  # type: (Registry) -> namedtuple
    """Returns namedtuple instance object has configuration."""
    get_value = get_config_value_fn(registry)

    defaults = [
        ('hsts_support', True),
        ('ssl_redirect', True),

        ('proto_header', ''),   # e.g. X-Forwarded-Proto
        ('ignore_paths', tuple()),

        # HSTS Header value
        ('hsts_max_age', '31536000'),  # seconds, 1 year
        ('hsts_include_subdomains', True),
        ('hsts_preload', True),
    ]

    # pylint: disable=invalid-name
    Config = namedtuple('Config', [k for k, _ in defaults])
    return Config(**dict([(k, get_value(k, v)) for k, v in defaults]))


def apply_ignore_filter(req, ignore_paths):  # type: (Request, tuple) -> bool
    if ignore_paths:
        return any([req.path.startswith(path) for path in ignore_paths])
    return False


def build_criteria(req, config):  # type: (Request, namedtuple) -> tuple
    """Builds criteria contains about incoming request."""
    criteria = [
        req.url.startswith('https://'),
    ]
    if config.proto_header:
        criteria.append(
            req.headers.get(config.proto_header, 'http') == 'https')

    return tuple(criteria)
