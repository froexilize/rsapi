import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='rsapi',
    version='0.2',
    author="Rasmart team",
    author_email="rasmarutil@gmail.com",
    description="api impl on python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rasmartguy/rsapi",
    packages=setuptools.find_packages(),
    install_requires=['racrypt==0.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
