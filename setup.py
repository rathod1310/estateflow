from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="estateflow",
    version="1.0.0",
    description="Mobile-first Real Estate CRM for ERPNext",
    author="EstateFlow",
    author_email="support@estateflow.in",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
