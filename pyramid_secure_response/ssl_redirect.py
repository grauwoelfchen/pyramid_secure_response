from pyramid.httpexceptions import HTTPMovedPermanently

from pyramid_secure_response.util import (
    logger,
    apply_ignore_filter,
    get_config,
    build_criteria,
)


def tween(handler, registry):
    """Redirects insecure http request as configured.

    This tween does not handle request if insecure request comes.
    """
    config = get_config(registry)

    tween_name = 'ssl_redirect'

    def _ssl_redirect_tween(req):
        if not config.ssl_redirect:
            return handler(req)

        if apply_ignore_filter(req, config.ignore_paths):
            logger.info('(%s) Ignored path %s', tween_name, req.path)
            return handler(req)

        criteria = build_criteria(req, config)
        secure = all(criteria)

        if secure:
            return handler(req)

        logger.warning('(%s) Insecure request %s', tween_name, req.url)

        raise HTTPMovedPermanently(location='https://{:s}{:s}'.format(
            req.host, req.path))

    return _ssl_redirect_tween
