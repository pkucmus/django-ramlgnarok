import os
from setuptools import find_packages, setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name='ramlgnarok',
    version='0.1',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    license='BSD',
    description='',
    long_description='',
    url='',
    author_email='pkucmus@gmail.com',
    extras_require={
        'develop': [
            'readline==6.2.4.1',
            'pdbpp==0.8.3',
            'ipdb==0.10.1',
            'ipython==5.1.0',
            'mock==2.0.0',
            'coverage==4.2',
        ]
    },
    install_requires=[
        'ramlfications==0.1.9',
        'markdown',
        'pygments'
    ],
    # entry_points={
    #     'console_scripts': [
    #         'ramlgnarok = ramlgnarok.service.runner:cli',
    #     ],
    # },
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.12',
    ],
)
