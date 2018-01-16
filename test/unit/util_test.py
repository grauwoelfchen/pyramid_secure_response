import pytest

from pyramid_secure_response.util import (
    get_config,
    apply_path_filter,
    build_criteria,
)


def test_get_config_keys(dummy_request):
    config = get_config(dummy_request.registry)
    expected_keys = (
        'proto_header',
        'ignore_paths',
        # tweens
        'ssl_redirect',
        'hsts_support',
        'csp_coverage',
    )
    assert expected_keys == tuple(config._asdict().keys())


@pytest.mark.parametrize('config_key,default_value', [
    ('proto_header', ''),
    ('ignore_paths', tuple()),
    ('ssl_redirect.enabled', True),
    ('ssl_redirect.proto_header', ''),
    ('ssl_redirect.ignore_paths', tuple()),
    ('hsts_support.enabled', True),
    ('hsts_support.proto_header', ''),
    ('hsts_support.ignore_paths', tuple()),
])
def test_get_config_defaults(dummy_request, config_key, default_value):
    config = get_config(dummy_request.registry)
    keys = config_key.split('.')
    if len(keys) == 1:
        assert default_value == getattr(config, keys[0])
    else:
        assert default_value == getattr(getattr(config, keys[0]), keys[1])


@pytest.mark.parametrize('paths', [
    tuple(),
    ('/foo', '/bar'),
    ('humans.txt', 'robots.txt'),
    ('/static/humans.txt',),
])
def test_apply_path_filter_as_not_ignored(dummy_request, paths):
    dummy_request.path = '/humans.txt'
    assert not apply_path_filter(dummy_request, paths)


@pytest.mark.parametrize('paths', [
    ('/humans.txt',),
    ('/humans.txt', '/robots.txt'),
])
def test_apply_path_filter_as_ignored(dummy_request, paths):
    dummy_request.path = '/humans.txt'
    assert apply_path_filter(dummy_request, paths)


@pytest.mark.parametrize('url,proto_header,header,value', [
    ('http://127.0.0.1/', '', None, None),
    ('http://127.0.0.1/', '', 'X-Forwarded-Proto', 'http'),
    ('http://127.0.0.1/', 'X-Forwarded-Proto', 'X-Forwarded-Proto', None),
    ('http://127.0.0.1/', 'X-Forwarded-Proto', 'X-Forwarded-Proto', 'http'),
    ('https://127.0.0.1/', 'X-Forwarded-Proto', 'X-Forwarded-Proto', None),
    ('https://127.0.0.1/', 'X-Forwarded-Proto', 'X-Forwarded-Proto', 'http'),
])
def test_criteria_not_all_secure(dummy_request, url, proto_header,
                                 header, value):
    from collections import namedtuple

    dummy_request.url = url
    dummy_request.headers[header] = value

    # pylint: disable=invalid-name
    Config = namedtuple('Config', 'proto_header')
    config = Config(proto_header)

    criteria = build_criteria(dummy_request, proto_header=config.proto_header)
    assert not all(criteria)


@pytest.mark.parametrize('url,proto_header,header,value', [
    ('https://127.0.0.1/', '', None, None),
    ('https://127.0.0.1/', '', 'X-Forwarded-Proto', 'https'),
    ('https://127.0.0.1/', 'X-Forwarded-Proto', 'X-Forwarded-Proto', 'https'),
])
def test_criteria_all_secure(dummy_request, url, proto_header,
                             header, value):
    from collections import namedtuple

    dummy_request.url = url
    dummy_request.headers[header] = value

    # pylint: disable=invalid-name
    Config = namedtuple('Config', 'proto_header')
    config = Config(proto_header)

    criteria = build_criteria(dummy_request, proto_header=config.proto_header)
    assert all(criteria)
