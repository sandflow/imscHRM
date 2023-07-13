from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setup(
  name='imschrm', 
  version='1.1.0b2',
  description='Validates IMSC documents against the IMSC HRM',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author='Sandflow Consulting LLC',
  author_email='info@sandflow.com',
  url='https://www.sandflow.com',
  project_urls={
    'Bug Reports': 'https://github.com/sandflow/imscHRM/issues',
    'Source': 'https://github.com/sandflow/imscHRM',
  },
  install_requires = ["ttconv>=1.0.1"],
  classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Multimedia'
  ],
  license_files = ['LICENSE.txt'],
  keywords='ttml, imsc, smpte-tt, hrm, complexity',
  package_dir={'': 'src/main/python'},
  packages=['imschrm'],
  entry_points = {
        'console_scripts': ['imschrm=imschrm.cli:main'],
  },
  python_requires='>=3.8, <4'
)
