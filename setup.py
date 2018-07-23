try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

tests_require = ['pytest']

long_description = """
Thredo is threads.
"""


setup(name="thredo",
      description="Thredo - Threads",
      long_description=long_description,
      license="MIT",
      version="0.0",
      author="David Beazley",
      author_email="dave@dabeaz.com",
      maintainer="David Beazley",
      maintainer_email="dave@dabeaz.com",
      url="https://github.com/dabeaz/thredo",
      packages=['thredo'],
      tests_require=tests_require,
      extras_require={
          'test': tests_require,
      },
      classifiers=[
          'Programming Language :: Python :: 3',
      ])
