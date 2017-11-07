import pytest

from pyramid_secure_response.ssl_redirect import tween


@pytest.fixture(autouse=True)
def setup():
    import logging
    from pyramid_secure_response.ssl_redirect import logger
    logger.setLevel(logging.ERROR)


def test_redirect_tween_ssl_redirect_off(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.ssl_redirect.apply_ignore_filter',
                 return_value=True)
    mocker.patch('pyramid_secure_response.ssl_redirect.build_criteria',
                 return_value=[])

    from pyramid_secure_response.ssl_redirect import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.registry.settings = {
        'pyramid_secure_response.ssl_redirect': 'False'
    }

    handler_stub = mocker.stub(name='handler_stub')
    ssl_redirect_tween = tween(handler_stub, dummy_request.registry)
    ssl_redirect_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 0 == apply_ignore_filter.call_count
    assert 0 == build_criteria.call_count


def test_redirect_tween_ignored_path(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.ssl_redirect.apply_ignore_filter',
                 return_value=True)
    mocker.patch('pyramid_secure_response.ssl_redirect.build_criteria',
                 return_value=[])

    from pyramid_secure_response.ssl_redirect import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.path = '/humans.txt'
    dummy_request.registry.settings = {
        'pyramid_secure_response.ssl_redirect': 'True',
        'pyramid_secure_response.ignore_paths': '\n/humans.txt\n'
    }

    handler_stub = mocker.stub(name='handler_stub')
    ssl_redirect_tween = tween(handler_stub, dummy_request.registry)
    ssl_redirect_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(
        dummy_request, ('/humans.txt',))
    assert 0 == build_criteria.call_count


def test_redirect_tween_insecure(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.ssl_redirect.apply_ignore_filter',
                 return_value=False)
    mocker.patch('pyramid_secure_response.ssl_redirect.build_criteria',
                 return_value=[False])

    from pyramid.httpexceptions import HTTPMovedPermanently

    from pyramid_secure_response.ssl_redirect import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.url = 'http://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.ssl_redirect': 'True',
    }

    handler_stub = mocker.stub(name='handler_stub')
    ssl_redirect_tween = tween(handler_stub, dummy_request.registry)

    with pytest.raises(HTTPMovedPermanently):
        ssl_redirect_tween(dummy_request)

    # pylint: disable=no-member
    assert 0 == handler_stub.call_count
    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())
    assert 1 == build_criteria.call_count


def test_redirect_tween_secure(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.ssl_redirect.apply_ignore_filter',
                 return_value=False)
    mocker.patch('pyramid_secure_response.ssl_redirect.build_criteria',
                 return_value=[True])

    from pyramid_secure_response.ssl_redirect import (
        apply_ignore_filter,
        build_criteria,
    )

    dummy_request.url = 'https://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.ssl_redirect': 'True',
    }

    handler_stub = mocker.stub(name='handler_stub')
    ssl_redirect_tween = tween(handler_stub, dummy_request.registry)
    ssl_redirect_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 1 == apply_ignore_filter.call_count
    apply_ignore_filter.assert_called_once_with(dummy_request, tuple())
    assert 1 == build_criteria.call_count
