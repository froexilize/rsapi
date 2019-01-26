import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='ra-api',
     version='0.1',
     scripts=['ra-api'] ,
     author="Rasmart team",
     author_email="rasmarutil@gmail.com",
     description="client api on python3",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/rasmartguy/ra-api",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )