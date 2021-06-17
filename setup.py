from setuptools import setup, find_packages
import pkg_resources
import pathlib

with open('README.md') as readme_file:
    README = readme_file.read()

setup_args = dict(
    name='ppe_match',
    version='0.1.0',
    description=' Intuitive framework that allows researchers to implement and test matching methodologies',
    long_description_content_type="text/markdown",
    long_description=README,
    license='MIT',
    packages=find_packages(),
    author='Ram Bala, Michele Samorani, Rohit Jacob',
    author_email='rbala@scu.edu, msamorani@scu.edu, rohitjacob92@gmail.com',
    keywords=['matching','ppe','framework','matcha','frappe'],
    url='https://github.com/samorani/MatchingPPE',
    include_package_data=True,
	package_data={'': ['data/*.csv']},
)

with pathlib.Path('requirements.txt').open() as requirements_txt:
    install_requires = [
        str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)
    ]

classifiers=[
  'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
  'Intended Audience :: Developers',      # Define that your audience are developers
  'Topic :: Software Development :: Build Tools',
  'License :: OSI Approved :: MIT License',   # Again, pick a license
  'Programming Language :: Python :: 3',      #Specify which python versions that you want to support
  'Programming Language :: Python :: 3.4',
  'Programming Language :: Python :: 3.5',
  'Programming Language :: Python :: 3.6',
  'Programming Language :: Python :: 3.7',
  'Programming Language :: Python :: 3.8'
]

if __name__ == '__main__':
    setup(**setup_args,
			install_requires=install_requires,
			classifiers=classifiers)
