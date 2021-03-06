# coding=utf-8
"""
    create by pymu
    on 2021/4/29
    at 16:30
    具体命令详解，请参阅：https://blog.konghy.cn/2018/04/29/setup-dot-py/
"""

from setuptools import setup, find_packages

from sherry_tooltip import version

info = {
    'project_urls': {
        'Documentation': 'https://github.com/py-mu/sherry-tooltip'
    },
    'name': 'sherry-tooltip',
    'version': '.'.join(map(str, version)),
    'description': 'Sherry event hook',
    'author': '黄大胆',
    'author_email': '1540235670@qq.com',
    'url': 'https://github.com/py-mu/sherry-tooltip',
    'license': 'Apache',
    'keywords': 'GUI'
}

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
]

with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    long_description=long_description,
    long_description_content_type="text/markdown",
    platforms=['OS-independent'],
    classifiers=classifiers,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['PyQt5'],
    python_requires='>=3.6',
    **info
)
