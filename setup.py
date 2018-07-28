from setuptools import setup
from Redy.Tools.Version import Version

with open('./README.rst', encoding='utf-8') as f:
    readme = f.read()

version_filename = 'next_version'
with open(version_filename) as f:
    version = Version(f.read().strip())

# @formatter:off
setup(name='rtpy',
      version=str(version),
      keywords='CLI solution',
      description="effective and intuitive CLI framework",
      long_description=readme,
      license='MIT',
      url='https://github.com/thautwarm/rtpy',
      author='thautwarm',
      author_email='twshere@outlook.com',
      include_package_data=True,
      install_requires=['Redy', 'rbnf', 'readline', 'linq-t'],
      packages=['rtpy.cmd', 'rtpy.weapon', 'rtpy.terminal', 'rtpyrc.terminal.private'],
      platforms='any',
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: Implementation :: CPython'],
      zip_safe=False
      )
# @formatter:on


version.increment(version_number_idx=2, increment=1)
if version[2] is 42:
    version.increment(version_number_idx=1, increment=1)
if version[1] is 42:
    version.increment(version_number_idx=0, increment=1)

with open(version_filename, 'w') as f:
    f.write(str(version))
