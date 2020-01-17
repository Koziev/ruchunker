import io
import setuptools

with io.open("README.md", mode="r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="ruchunker",
    version="0.0.9",
    author="Ilya Koziev",
    author_email="inkoziev@gmail.com",
    description="Chunker for Russian language",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Koziev/ruchunker",
    packages=setuptools.find_packages(),
    package_data={'ruchunker': ['chunker_NP.config', 'chunker_NP.model']},
    include_package_data=True,
   
)
