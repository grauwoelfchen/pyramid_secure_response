from pyramid_secure_response.util import (
    logger,
    apply_path_filter,
    get_config,
    build_criteria,
)

HEADER_KEY = 'Strict-Transport-Security'


def build_hsts_header(config):
    """Returns HSTS Header value."""
    value = 'max-age={0}'.format(config.max_age)
    if config.include_subdomains:
        value += '; includeSubDomains'
    if config.preload:
        value += '; preload'
    return value


def tween(handler, registry):
    r"""Sets HTTP Strict Transport Security Header as configured.

    About details of HSTS, see below:

    * https://hstspreload.org/
    * https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/\
        Strict-Transport-Security#Preloading_Strict_Transport_Security
    """
    config = get_config(registry)

    hsts_support = config.hsts_support

    ignore_paths = config.ignore_paths
    if hsts_support.ignore_paths:
        ignore_paths = hsts_support.ignore_paths

    proto_header = config.proto_header
    if hsts_support.proto_header:
        proto_header = hsts_support.proto_header

    tween_name = 'hsts_support'

    def _hsts_support_tween(req):
        if not hsts_support.enabled:
            return handler(req)

        # ignore
        if apply_path_filter(req, ignore_paths):
            logger.info('(%s) Ignore path %s', tween_name, req.path)
            return handler(req)

        criteria = build_criteria(req, proto_header=proto_header)
        secure = all(criteria)

        if not secure:
            # sets the header only for https
            logger.warning('(%s) Insecure request %s', tween_name, req.url)
            return handler(req)

        res = handler(req)

        if HEADER_KEY not in res.headers:
            # ignore if already exists
            res.headers[HEADER_KEY] = build_hsts_header(hsts_support)

        return res

    return _hsts_support_tween
