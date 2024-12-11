from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="cq.jwt-compress",
    version="1.1.0",
    packages=["cq.jwt_compress"],
    namespace_packages=["cq"],
    package_dir={"": "src"},
    package_data={"": []},
    include_package_data=True,
    url="https://github.com/carrotquest/cq.jwt-compress",
    license="MIT License",
    author="Mikhail Shvein",
    author_email="m1ha@dashly.io",
    description="JWT roles compress algorithms",
    long_description=long_description,
    long_description_content_type="text/markdown"
)
