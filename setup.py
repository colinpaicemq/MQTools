from setuptools import setup
#from distutils.core import setup, Extension

setup(name = 'mqtools',
    version = '0.1',
    description = 'Python code providing utilities including creating and parsing IBM MQ PCF.',
    long_description= 'Python code providing utilities including creating and parsing IBM MQ PCF.',
    author='Colin Paice',
    author_email='colinpaicemq@gmail.com',
    url='https://github.com/colinpaicemq/MQTools/',
    download_url='https://github.com/colinpaicemq/MQTools/',
    platforms='OS Independent',
    #packages = find_packages('pymqi'),
    packages = ['mqtools'],
    license='Python Software Foundation License',
    keywords=('MQ IBM PCF'),
    include_package_data=True,
    #nstall_requires = ["pymqi"],

    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Python Software Foundation License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
   )
