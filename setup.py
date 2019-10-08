import setuptools

with open("README.md", "r") as fh:
    long_desciption = fh.read()

setuptools.setup(
    name="pydoom",
    version="1.0.0",
    author="sven7",
    author_email="x_dotor@163.com",
    description="data check",
    long_desciption=long_desciption,
    long_desciption_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[],
    python_requires=">=3.6",
)
