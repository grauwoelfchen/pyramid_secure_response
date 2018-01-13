import re
from pyramid_secure_response.util import (
    logger,
    apply_path_filter,
    get_config,
)

HEADER_KEY = 'Content-Security-Policy'

# MIME types
# * https://developer.mozilla.org/en-US/docs/Web/HTTP/\
#     Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
# * https://www.iana.org/assignments/media-types/media-types.xhtml
MIME_TYPE_PATTERN = re.compile(r'\A[-\w]+\/[-\w]+\Z')

# SCHEME
# colon at the end is required
SCHEME_VALUES = (
    'blob:',
    'data:',
    'filesystem:',
    'http:',
    'https:',
    'mediastream:',
)

# sandbox
# this directive is not supported in <meta> element and
# 'Content-Security-Policy-Report-Only'.
SANDBOX_VALUES = (
    'allow-forms',
    'allow-modals',
    'allow-orientation-lock',
    'allow-pointer-lock',
    'allow-popups',
    'allow-popups-to-escape-sandbox',
    'allow-presentation',
    'allow-same-origin',
    'allow-scripts',
    'allow-top-navigation',
)

# directives
NO_QUOTE_DIRECTIVES = (
    'report-uri', 'report-to',
    'plugin-types'
)

BOOLEAN_DIRECTIVES = (
    'block-all-mixed-content', 'upgrade-insecure-requests'
)


def _build_csp_header_value(directive, texts):
    """Creates CSP Header values for directive from texts.

    Returns empty string if does not valid directive or texts is given.
    """
    if texts:
        if directive in BOOLEAN_DIRECTIVES:
            # bool value
            if texts.lower() == 'true':
                return '{0:s}'.format(directive)
        else:
            values = []
            for text in texts.split(' '):
                # schemes <scheme-source>, mime type <type>/<subtype> and
                # sandbox <value> shouldn't be surrounded with single
                # quotes
                if not text.startswith(SCHEME_VALUES) and \
                   text not in SANDBOX_VALUES and \
                   (directive not in NO_QUOTE_DIRECTIVES and
                    not MIME_TYPE_PATTERN.match(text)) and \
                   '\'' not in text:
                    text = "'{:s}'".format(text)

                values.append(text)

            return '{0:s} {1:s}'.format(directive, ' '.join(values))

    return ''


def build_csp_header(config):  # type: (Union[namedtuple, dict]) -> str
    """Returns CSP Header values."""
    policy_text = ''

    config_dict = config

    # namedtuple
    if isinstance(config, tuple) and hasattr(config, '_asdict'):
        config_dict = config._asdict()

    if not isinstance(config_dict, dict):
        raise ValueError

    for name in config_dict:
        if name in ('enabled', 'ignore_paths'):  # not directive
            continue

        value = _build_csp_header_value(
            name.replace('_', '-'), str(config_dict[name]))
        if value:
            policy_text += '; {:s}'.format(value)

    return policy_text[2:]


def tween(handler, registry):
    r"""Sets Content Security Policy Header as configured.

    About details of CSP, see below:

    * https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
    * https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/\
        Content-Security-Policy
    """
    config = get_config(registry)

    csp_coverage = config.csp_coverage

    ignore_paths = config.ignore_paths
    if csp_coverage.ignore_paths:
        ignore_paths = csp_coverage.ignore_paths

    tween_name = 'csp_coverage'

    def _csp_coverage_tween(req):
        if not config.csp_coverage.enabled:
            return handler(req)

        if apply_path_filter(req, ignore_paths):
            logger.info('(%s) Ignore path %s', tween_name, req.path)
            return handler(req)

        res = handler(req)
        if HEADER_KEY not in res.headers:
            # ignore if already exists
            header_value = build_csp_header(csp_coverage)
            if header_value:
                res.headers[HEADER_KEY] = header_value

        return res

    return _csp_coverage_tween
