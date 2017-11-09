from pyramid_secure_response.util import (
    logger,
    apply_ignore_filter,
    get_config,
    build_criteria,
)


def build_hsts_header(config):
    """Returns HSTS Header value."""
    value = 'max-age={0}'.format(config.hsts_max_age)
    if config.hsts_include_subdomains:
        value += '; includeSubDomains'
    if config.hsts_preload:
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

    tween_name = 'hsts_support'

    def _hsts_support_tween(req):
        if not config.hsts_support:
            return handler(req)

        if apply_ignore_filter(req, config.ignore_paths):
            logger.info('(%s) Ignored path %s', tween_name, req.path)
            return handler(req)

        criteria = build_criteria(req, config)
        secure = all(criteria)

        # Sets the header only for https
        if not secure:
            logger.warning('(%s) Insecure request %s', tween_name, req.url)
            return handler(req)

        res = handler(req)
        res.headers['Strict-Transport-Security'] = build_hsts_header(config)

        return res

    return _hsts_support_tween
