try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

tests_require = ['pytest']

setup(name = "freddy",
            description="freddy - json filtering",
            long_description = """
freddy is a library for ideas in filtering json
""",
            license="""MIT""",
            version = "0.1",
            author = "Gary Anderson",
            maintainer = "Gary Anderson",
            url = "https://github.com/gando999/freddy",
            packages = ['freddy'],
            tests_require = tests_require,
            extras_require = {
                'test': tests_require,
              },
            classifiers = [
              'Programming Language :: Python :: 2.7',
              ]
            )
