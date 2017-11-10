from pyramid import tweens

__all__ = (
    '__version__',
    '__name__',  # pylint: disable=undefined-all-variable
)

__version__ = '0.0.4'


def includeme(config):
    """Includes all twees that are provided by `pyramid_secure_response`.

    >>> from pyramid.config import Configurator
    >>> config = Configurator(settings={})

    >>> config.include('pyramid_secure_response')

    Otherwise, use just `add_tween()` as you need.

    >>> config.add_tween('pyramid_secure_response.ssl_redirect.tween')
    >>> config.add_tween('pyramid_secure_response.hsts_support.tween')
    """
    tween_name = (lambda name: '{:s}.{:s}.tween'.format(__name__, name))

    config.add_tween(tween_name('ssl_redirect'),
                     over=tweens.MAIN)

    config.add_tween(tween_name('hsts_support'),
                     over=tweens.MAIN,
                     under=tween_name('ssl_redirect'))
