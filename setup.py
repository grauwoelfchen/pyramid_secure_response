import os

from setuptools import setup, find_packages


# pylint: disable=invalid-name
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, *('doc', 'DESCRIPTION.rst'))) as f:
        DESCRIPTION = f.read()
    with open(os.path.join(here, 'CHANGELOG')) as f:
        CHANGES = f.read()
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
    description='pyramid_secure_response',
    long_description=DESCRIPTION + '\n\n' + CHANGELOG,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
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
