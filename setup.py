import os

from setuptools import setup, find_packages


# pylint: disable=invalid-name
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, *('doc', 'DESCRIPTION.rst'))) as f:
        DESCRIPTION = f.read()
    with open(os.path.join(here, 'CHANGELOG')) as f:
        CHANGELOG = f.read()
except IOError:
    DESCRIPTION = ''
    CHANGELOG = ''


def file_path(name):
    return os.path.join(os.path.dirname(__file__), name)


def read_file(path):
    return open(path, 'r').read()


def get_attr(name, attr):
    import re

    pattern = r"{0}\s=\s'([^']+)'".format(attr)
    value, = re.findall(pattern, read_file(file_path(name)))
    return value


requires = [
    'pyramid',
]

development_requires = [
    'flake8',
    'flake8_docstrings',
    'pycodestyle',
    'pylint',
]

testing_requires = [
    'pytest',
    'pytest-cov',
    'pytest-mock',
]

documentation_requires = [
]

setup(
    name='pyramid_secure_response',
    version=get_attr('pyramid_secure_response/__init__.py', '__version__'),
    description='A library redirects non-http as https, sets hsts header.',
    long_description=DESCRIPTION + '\n\n' + CHANGELOG,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
    ],
    author='Yasuhiro Asaka',
    author_email='yasuhiro.asaka@grauwoelfchen.net',
    url='https://gitlab.com/grauwoelfchen/pyramid_secure_response',
    keywords='web wsgi pylons pyramid',
    license='BSD-3-Clause',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'development': development_requires,
        'testing': testing_requires,
        'documentation': documentation_requires,
    },
    install_requires=requires,
    entry_points='',
)
