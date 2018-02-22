from setuptools import setup, find_packages

setup(
    name='speccy-parser',
    version='0.1.0',
    python_requires=">=3.4",
    description="A simple library for parsing a Speccy snapshot",
    url='https://github.com/linuxdaemon/speccy-parser',
    author='linuxdaemon',
    author_email='linuxdaemon@snoonet.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='speccy parser requests',
    packages=find_packages(),
    install_requires=['requests', 'bs4', 'lxml'],
    setup_requires=[],
    tests_require=[],
)
