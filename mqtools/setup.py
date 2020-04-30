from distutils.core import setup, Extension

include_dirs = ['/opt/mqm/inc']

module1 = Extension('spam',
                    sources = ['spamsystem.c'],
                                include_dirs = include_dirs,

)

setup (name = 'PackageName',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
