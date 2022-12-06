import setuptools

with open("README.md", "r") as fh:
	description = fh.read()

setuptools.setup(
	name="netlister",
	version="0.0.1",
	author="dehekkendekrekker",
	author_email="donotdisturb@nowhere.else",
	packages=["netlister"],
	description="Turns yosys output into KiCad6 netlist",
	long_description=description,
	long_description_content_type="text/markdown",
	url="https://github.com/dehekkendekrekker/netlister.git",
	license='MIT',
	python_requires='>=3.8',
	install_requires=['loguru','colored','prettytable','skidl'],
    entry_points = {
        'console_scripts': [
            'mknl = netlister:run'
        ]
    }
)