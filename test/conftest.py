import pytest


@pytest.fixture(scope='function')
def dummy_request():  # type: () -> Request
    from pyramid import testing

    url = 'http://example.org'
    settings = {}
    req = testing.DummyRequest(
        environ={},
        locale_name='en',
        matched_route=None,
        settings=settings,
        server_name='example.org',
        subdomain='',
        host='example.org:80',
        application_url=url,
        url=url,
        host_url=url,
        path_url=url,
    )
    req.registry.settings = settings
    return req
