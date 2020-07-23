from setuptools import find_packages, setup
setup(name='appsec',
      version='0.1',
      packages=find_packages(),
      package_data={
            'appsec': ['templates/*', 'spell/*']
      },
      install_requires=['flask', 'Flask-WTF'],
      extras_require={"test": ["pytest", "coverage"]}
      )
