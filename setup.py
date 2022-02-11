import setuptools

setuptools.setup(
    name="streamlit-forum",
    version="0.0.1",
    author="Snehan Kekre",
    author_email="snehan@streamlit.io",
    description="Streamlit component to display topics from Streamlit's community forum related to any exception.",
    long_description="Streamlit component to display topics from Streamlit's community forum related to any exception.",
    long_description_content_type="text/plain",
    url="https://github.com/snehankekre/streamlit-forum",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.6",
    install_requires=["streamlit >= 1.0.0", "requests >= 2.20.0"]
)
