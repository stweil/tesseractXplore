from itertools import chain
from setuptools import setup, find_packages
from naturtag import __version__

extras_require = {
    'ui': ['kivy>=1.11', 'kivymd~=0.104.1', 'pygments'],
    'dev': [
        'black',
        'kivy_examples',
        'memory_profiler',
        'prettyprinter',
        'pytest',
        'Sphinx>=3.0',
        'sphinx-autodoc-typehints',
        'sphinx-rtd-theme',
        'sphinxcontrib-apidoc',
    ],
}
extras_require['all'] = list(chain.from_iterable(extras_require.values()))
extras_require['ui-win'] = ['pypiwin32', 'kivy_deps.sdl2', 'kivy_deps.gstreamer', 'kivy_deps.angle']
extras_require['all-win'] = extras_require['all'] + extras_require['ui-win']

setup(
    name='naturtag',
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'appdirs',
        'attrs',
        'Click>=7.0',
        'click-help-colors',
        'pillow>=7.0',
        'pyexiv2',
        # 'pyinaturalist',  # TODO: Submit PR(s) for WIP pyinaturalist changes
        'pyinaturalist @ git+https://github.com/JWCook/pyinaturalist.git@dev',
        'pyyaml',
        'requests',
        'requests-cache',
        'xmltodict',
    ],
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'naturtag=naturtag.cli:main',
            'nt=naturtag.cli:main',
        ],
        'gui_scripts': [
            'naturtag-ui=naturtag.ui.app:main',
        ],
    }
)
