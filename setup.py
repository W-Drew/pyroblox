from setuptools import setup

setup(
	name = "pyroblox",
	version = "0.1",
	description = "",
	url = "https://github.com/EchoReaper/pyroblox",
	author = "Drew Warwick",
	author_email = "dwarwick96@gmail.com",
	license = "Apache 2.0",
	packages=["pyroblox"],
	install_requires = [
		"requests","bs4","python-dateutil"
	],
	zip_safe=False
)