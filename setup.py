from setuptools import setup, find_packages


version = '1.0'


tests_require = [
    'unittest2',
    'mocker',
    'nose',
    ]


setup(name='github-watchlist',
      version=version,
      description='Manage your watched GitHub repositories per script',
      long_description=open('README.rst').read(),

      classifiers=[
        'Intended Audience :: Developers',
        ],

      keywords='github watchlist',
      author='Jonas Baumann',
      url='https://github.com/jone/github-watchlist',

      license='Beerware',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=False,

      install_requires=[
        'argparse',
        'requests',
        'setuptools',
        ],

      tests_require=tests_require,
      extras_require={'tests': tests_require},

      entry_points = {
        'console_scripts' : [
            'initalize = watchlist.initialize:initalize_command',
            ]})
