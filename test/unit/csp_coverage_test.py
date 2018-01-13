import pytest

from pyramid_secure_response.csp_coverage import tween


@pytest.fixture(autouse=True)
def setup():
    import logging
    from pyramid_secure_response.csp_coverage import logger
    logger.setLevel(logging.ERROR)


@pytest.mark.parametrize('directives,header', [
    # [fetch directive]
    ({},
     ""),
    ({'child_src': 'self', 'default_src': 'none'},
     "child-src 'self'; default-src 'none'"),
    ({'connect_src': 'self', 'default_src': 'none'},
     "connect-src 'self'; default-src 'none'"),
    ({'default_src': ''},
     ""),
    ({'default_src': 'https:'},
     "default-src https:"),
    ({'default_src': "self https://example.org/"},
     "default-src 'self' https://example.org/"),
    ({'default_src': 'none'},
     "default-src 'none'"),
    ({'font_src': 'unsafe-inline'},
     "font-src 'unsafe-inline'"),
    ({'frame_src': 'unsafe-eval'},
     "frame-src 'unsafe-eval'"),
    ({'img_src': 'strict-dynamic'},
     "img-src 'strict-dynamic'"),
    ({'manifest_src': 'nonce-2726c7f26c'},
     "manifest-src 'nonce-2726c7f26c'"),
    ({'media_src': (
        'sha256-076c8f1ca6979ef156b510a121b69b626'
        '5011597557ca2971db5ad5a2743545f')},
     "media-src '{:s}'".format(
         'sha256-076c8f1ca6979ef156b510a121b69b626'
         '5011597557ca2971db5ad5a2743545f')),
    ({'object_src': '*'},
     "object-src '*'"),
    ({'script_src': 'https://example.org/'},
     "script-src https://example.org/"),
    ({'style_src': 'self'},
     "style-src 'self'"),
    ({'worker_src': 'self https://example.org/ https://example.com/'},
     "worker-src 'self' https://example.org/ https://example.com/"),
    # [document directive]
    ({'base_uri': 'self', 'default_src': 'none'},
     "default-src 'none'; base-uri 'self'"),
    ({'plugin_types': 'application/x-schockwave-flash', 'object_src': ''},
     "plugin-types application/x-schockwave-flash"),
    ({'plugin_types': 'application/xhtml+xml', 'object_src': ''},
     "plugin-types application/xhtml+xml"),
    ({'plugin_types': 'application/vnd.mozilla.xul+xml', 'object_src': ''},
     "plugin-types application/vnd.mozilla.xul+xml"),
    ({'plugin_types': 'video/3gpp2', 'object_src': ''},
     "plugin-types video/3gpp2"),
    ({'sandbox': 'allow-forms'},
     "sandbox allow-forms"),
    # [navigation directive]
    ({'form_action': 'self'},
     "form-action 'self'"),
    ({'frame_ancestors': 'self'},
     "frame-ancestors 'self'"),
    ({'default_src': 'https:',
      'report_uri': '/csp-violation-report-endpoint/'},
     "default-src https:; report-uri /csp-violation-report-endpoint/"),
    ({'default_src': 'https:',
      'report_to': '/csp-violation-report-endpoint/'},
     "default-src https:; report-to /csp-violation-report-endpoint/"),
    # - block_all_mixed_content
    # - referrer
    # - require_sri_for
    # - upgrade_insecure_requests
])
def test_build_csp_header(directives, header, dummy_request):
    from pyramid_secure_response.util import get_config
    from pyramid_secure_response.csp_coverage import build_csp_header

    dummy_request.url = 'http://example.org/'
    settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'True',
    }
    for key, value in directives.items():
        settings['pyramid_secure_response.csp_coverage.{:s}'.format(
            key)] = value

    dummy_request.registry.settings = settings
    config = get_config(dummy_request.registry)

    # NOTE:
    # [fetch]
    # - connect_src
    # - default_src
    # - font_src
    # - frame_src
    # - img_src
    # - manifest_src
    # - media_src
    # - object_src
    # - script_src
    # - style_src
    # - worker_src
    # [document]
    # - base_uri
    # - plugin_types
    # - sandbox
    # [navigation]
    # - form_action
    # - frame_ancestors
    # [reporting]
    # - report_uri
    # - report_to
    # [other]
    # - block_all_mixed_content
    # - referrer
    # - require_sri_for
    # - upgrade_insecure_requests
    assert header == build_csp_header(config.csp_coverage)


def test_build_csp_header_config_argument():
    from collections import namedtuple
    from pyramid_secure_response.csp_coverage import build_csp_header

    with pytest.raises(ValueError):
        build_csp_header('not dict or namedtuple')

    with pytest.raises(ValueError):
        build_csp_header(tuple())

    assert '' == build_csp_header({})

    # pylint: disable=invalid-name
    Config = namedtuple('Config', 'enabled')
    assert '' == build_csp_header(Config(True))


def test_csp_coverage_tween_with_disabled(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.csp_coverage.apply_path_filter',
                 return_value=True)

    from pyramid.response import Response
    from pyramid_secure_response.csp_coverage import (
        apply_path_filter,
    )

    dummy_request.registry.settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'False'
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    csp_coverage_tween = tween(handler_stub, dummy_request.registry)
    res = csp_coverage_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 0 == apply_path_filter.call_count
    assert 'Content-Security-Policy' not in res.headers


def test_csp_coverage_tween_with_ignored_path(mocker, dummy_request):
    mocker.patch('pyramid_secure_response.csp_coverage.apply_path_filter',
                 return_value=True)

    from pyramid.response import Response
    from pyramid_secure_response.csp_coverage import (
        apply_path_filter,
    )

    dummy_request.path = '/humans.txt'
    dummy_request.registry.settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'True',
        'pyramid_secure_response.csp_coverage.ignore_paths': '\n/humans.txt\n'
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    csp_coverage_tween = tween(handler_stub, dummy_request.registry)
    res = csp_coverage_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count
    assert 1 == apply_path_filter.call_count
    apply_path_filter.assert_called_once_with(
        dummy_request, ('/humans.txt',))
    assert 'Content-Security-Policy' not in res.headers


def test_csp_coverage_with_default_values(mocker, dummy_request):
    from pyramid_secure_response import csp_coverage
    mocker.spy(csp_coverage, 'apply_path_filter')

    from pyramid.response import Response
    from pyramid_secure_response.csp_coverage import (
        apply_path_filter,
    )

    dummy_request.url = 'http://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'True',
        'pyramid_secure_response.csp_coverage.ignore_paths': '\n',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    csp_coverage_tween = tween(handler_stub, dummy_request.registry)
    res = csp_coverage_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_path_filter.call_count
    apply_path_filter.assert_called_once_with(dummy_request, tuple())

    # does not set if header is empty
    assert 'Content-Security-Policy' not in res.headers


def test_csp_coverage_tween_default_src_with_host_source(
        mocker, dummy_request):
    from pyramid_secure_response import csp_coverage
    mocker.spy(csp_coverage, 'apply_path_filter')

    from pyramid.response import Response
    from pyramid_secure_response.csp_coverage import (
        apply_path_filter,
    )

    dummy_request.url = 'https://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'True',
        'pyramid_secure_response.csp_coverage.ignore_paths': '\n',
        'pyramid_secure_response.csp_coverage.default_src':
            'https://example.org/',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    csp_coverage_tween = tween(handler_stub, dummy_request.registry)
    res = csp_coverage_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_path_filter.call_count
    apply_path_filter.assert_called_once_with(dummy_request, tuple())

    assert 'Content-Security-Policy' in res.headers
    assert 'default-src https://example.org/' == \
        res.headers['Content-Security-Policy']


def test_csp_coverage_tween_default_src_with_scheme_source(
        mocker, dummy_request):
    from pyramid_secure_response import csp_coverage
    mocker.spy(csp_coverage, 'apply_path_filter')

    from pyramid.response import Response
    from pyramid_secure_response.csp_coverage import (
        apply_path_filter,
    )

    dummy_request.url = 'https://example.org/'
    dummy_request.registry.settings = {
        'pyramid_secure_response.csp_coverage.enabled': 'True',
        'pyramid_secure_response.csp_coverage.ignore_paths': '\n',
        'pyramid_secure_response.csp_coverage.default_src': 'https:',
    }

    handler_stub = mocker.stub(name='handler_stub')
    handler_stub.return_value = Response(status=200)
    csp_coverage_tween = tween(handler_stub, dummy_request.registry)
    res = csp_coverage_tween(dummy_request)

    # pylint: disable=no-member
    assert 1 == handler_stub.call_count

    assert 1 == apply_path_filter.call_count
    apply_path_filter.assert_called_once_with(dummy_request, tuple())

    assert 'Content-Security-Policy' in res.headers
    assert 'default-src https:' == \
        res.headers['Content-Security-Policy']
