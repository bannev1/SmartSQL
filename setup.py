import setuptools
import sys

if tuple(sys.version_info)[:2] < (3, 10):
	print('Sorry, Python versions older 3.10 are not supported, please install a later version of Python')
	sys.exit(-1)


def readme() -> str:
	try:
		with open('./README.md') as f:
			return f.read()
	except IOError:
		return ''


setuptools.setup(
	name='SmartSQL',
	version='v1.0.0',
	description='Control your SQL server with natural language',
	author='Valentina Banner',
	long_description=readme(),
	long_description_content_type='text/markdown',
	keywords='AI SQL',
	url='https://github.com/bannev1/SmartSQL',
	package_dir={'': 'src'},
	packages=setuptools.find_packages('src'),
	include_package_data=True,
	python_requires='>=3.10.0',
	install_requires=[
		"openai>=1.97.0",
		"dotenv>=0.9.9",
		"oracledb>=3.2.0",
		"psycopg2>=2.9.10"
	]
)