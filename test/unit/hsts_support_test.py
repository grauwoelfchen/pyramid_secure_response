import pytest

from pyramid_secure_response.hsts_support import tween


@pytest.fixture(autouse=True)
def setup():
    import logging
    from pyramid_secure_response.hsts_support import logger
    logger.setLevel(logging.ERROR)


@pytest.mark.parametrize('max_age,include_subdomains,preload,header', [
    ('3600', True, True, 'max-age=3600; includeSubDomains; preload'),
    ('1800', True, False, 'max-age=1800; includeSubDomains'),
    ('900', False, False, 'max-age=900'),
])
def test_build_hsts_header(max_age, include_subdomains, preload, header):
    from collections import namedtuple
    from pyramid_secure_response.hsts_support import build_hsts_header

    Config = namedtuple('Config', (  # pylint: disable=invalid-name
        'hsts_max_age',
        'hsts_include_subdomains',
        'hsts_preload',
    ))
    config = Config(max_age, include_subdomains, preload)

    assert header == build_hsts_header(config)


def test_hsts_support_tween_with_disabled(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.hsts_support.apply_ignore_filter',
                 return_value=True)
    mocker.patch('pyramid_secure_response.hsts_support.build_criteria',
                 return_value=[])

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'False'
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 0 == apply_ignore_filter.call_count
    assert 0 == build_criteria.call_count
    assert 'Strict-Transport-Security' not in res.headers


def test_hsts_support_tween_with_ignored_path(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.hsts_support.apply_ignore_filter',
                 return_value=True)
    mocker.patch('pyramid_secure_response.hsts_support.build_criteria',
                 return_value=[])

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.path = '/humans.txt'
    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'True',
        'pyramid_secure_response.ignore_paths': '\n/humans.txt\n'
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(
        dummy_request, ('/humans.txt',))
    assert 0 == build_criteria.call_count
    assert 'Strict-Transport-Security' not in res.headers


def test_hsts_tween_with_none_ssl_request(mocker, dummy_request):
    from pyramid_secure_response import hsts_support
    mocker.spy(hsts_support, 'apply_ignore_filter')
    mocker.spy(hsts_support, 'build_criteria')

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    from pyramid_secure_response.util import get_config

    dummy_request.url = 'http://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'True',
        'pyramid_secure_response.hsts_max_age': '31536000',
        'pyramid_secure_response.hsts_include_subdomains': 'True',
        'pyramid_secure_response.hsts_preload': 'True',
        'pyramid_secure_response.proto_header': '',
        'pyramid_secure_response.ignore_paths': '\n',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())

    assert 1 == build_criteria.call_count
    config = get_config(dummy_request.registry)
    build_criteria.assert_called_once_with(dummy_request, config)

    assert 'Strict-Transport-Security' not in res.headers


def test_hsts_tween_with_ssl_request_plus_none_ssl_extra_header(
        mocker, dummy_request):
    from pyramid_secure_response import hsts_support
    mocker.spy(hsts_support, 'apply_ignore_filter')
    mocker.spy(hsts_support, 'build_criteria')

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    from pyramid_secure_response.util import get_config

    dummy_request.url = 'https://example.org/'
    dummy_request.headers['X-Forwarded-Proto'] = 'http'
    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'True',
        'pyramid_secure_response.hsts_max_age': '3600',
        'pyramid_secure_response.hsts_include_subdomains': 'True',
        'pyramid_secure_response.hsts_preload': 'True',
        'pyramid_secure_response.proto_header': 'X-Forwarded-Proto',
        'pyramid_secure_response.ignore_paths': '\n',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())

    assert 1 == build_criteria.call_count
    config = get_config(dummy_request.registry)
    build_criteria.assert_called_once_with(dummy_request, config)

    assert 'Strict-Transport-Security' not in res.headers


def test_hsts_tween_with_ssl_request(mocker, dummy_request):
    from pyramid_secure_response import hsts_support
    mocker.spy(hsts_support, 'apply_ignore_filter')
    mocker.spy(hsts_support, 'build_criteria')

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    from pyramid_secure_response.util import get_config

    dummy_request.url = 'https://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'True',
        'pyramid_secure_response.hsts_max_age': '300',  # 5 minutes
        'pyramid_secure_response.hsts_include_subdomains': 'True',
        'pyramid_secure_response.hsts_preload': 'True',
        'pyramid_secure_response.proto_header': '',
        'pyramid_secure_response.ignore_paths': '\n',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())

    assert 1 == build_criteria.call_count
    config = get_config(dummy_request.registry)
    build_criteria.assert_called_once_with(dummy_request, config)

    assert 'Strict-Transport-Security' in res.headers
    assert 'max-age=300; includeSubDomains; preload' == \
        res.headers['Strict-Transport-Security']


def test_hsts_tween_with_ssl_request_plus_extra_header_check(
        mocker, dummy_request):
    from pyramid_secure_response import hsts_support
    mocker.spy(hsts_support, 'apply_ignore_filter')
    mocker.spy(hsts_support, 'build_criteria')

    from pyramid.response import Response
    from pyramid_secure_response.hsts_support import (
        apply_ignore_filter,
        build_criteria,
    )

    from pyramid_secure_response.util import get_config

    dummy_request.url = 'https://example.org/'
    dummy_request.headers['X-Forwarded-Proto'] = 'https'
    dummy_request.registry.settings = {
        'pyramid_secure_response.hsts_support': 'True',
        'pyramid_secure_response.hsts_max_age': '604800',  # 1 week
        'pyramid_secure_response.hsts_include_subdomains': 'True',
        'pyramid_secure_response.hsts_preload': 'True',
        'pyramid_secure_response.proto_header': 'X-Forwarded-Proto',
        'pyramid_secure_response.ignore_paths': '\n',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    hsts_support_tween = tween(handler_stub, dummy_request.registry)
    res = hsts_support_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())

    assert 1 == build_criteria.call_count
    config = get_config(dummy_request.registry)
    build_criteria.assert_called_once_with(dummy_request, config)

    assert 'Strict-Transport-Security' in res.headers
    assert 'max-age=604800; includeSubDomains; preload' == \
        res.headers['Strict-Transport-Security']
