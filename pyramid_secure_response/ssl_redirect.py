from pyramid.httpexceptions import HTTPMovedPermanently

from pyramid_secure_response.util import (
    logger,
    apply_path_filter,
    get_config,
    build_criteria,
)


def tween(handler, registry):
    """Redirects insecure HTTP request as configured.

    This tween does not handle request if insecure request comes.
    """
    config = get_config(registry)

    ssl_redirect = config.ssl_redirect

    ignore_paths = config.ignore_paths
    if ssl_redirect.ignore_paths:
        ignore_paths = ssl_redirect.ignore_paths

    proto_header = config.proto_header
    if ssl_redirect.proto_header:
        proto_header = ssl_redirect.proto_header

    tween_name = 'ssl_redirect'

    def _ssl_redirect_tween(req):
        if not ssl_redirect.enabled:
            return handler(req)

        # ignore
        if apply_path_filter(req, ignore_paths):
            logger.info('(%s) Ignore path %s', tween_name, req.path)
            return handler(req)

        criteria = build_criteria(req, proto_header=proto_header)
        secure = all(criteria)

        if secure:
            return handler(req)

        logger.warning('(%s) Insecure request %s', tween_name, req.url)

        raise HTTPMovedPermanently(location='https://{:s}{:s}'.format(
            req.host, req.path))

    return _ssl_redirect_tween
