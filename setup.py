from setuptools import setup

with open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='wisepy2',
    version="1.0.3",
    keywords='CLI solution',
    description="simple CLI framework",
    long_description=readme,
    license='MIT',
    url='https://github.com/Xython/wisepy2',
    author='thautwarm',
    author_email='twshere@outlook.com',
    py_modules=["wisepy2"],
    platforms='any',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    zip_safe=False)
