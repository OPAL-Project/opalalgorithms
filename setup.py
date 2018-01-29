# coding=utf-8

from setuptools import setup

setup(
    name='opalalgorithms',
    version='0.1.0',
    description='OPAL Algorithms. Package to implement algorithms to be run '
                'on OPAL platform.',
    author='Shubham Jain, Axel Oehmichen, Yves-Alexandre De Montjoye',
    author_email='shubhamjain0594@gmail.com',
    url='https://github.com/shubhamjain0594/opalalgorithms',
    license='MIT',
    packages=[
        'opalalgorithms',
        'opalalgorithms.core',
        'opalalgorithms.utils'
    ],
    include_package_data=True,
    install_requires=['setuptools'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License (MIT)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    keywords='python2, python3, opal, opalalgorithms',
)
