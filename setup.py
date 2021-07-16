# coding=utf-8
"""
    create by pymu
    on 2021/4/29
    at 16:30
    具体命令详解，请参阅：https://blog.konghy.cn/2018/04/29/setup-dot-py/
"""

from setuptools import setup, find_packages

info = {
    'project_urls': {
        'Documentation': 'https://github.com/py-mu/sherry-tooltip'
    },
    'name': 'sherry-tooltip',
    'version': '1.0.0',
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

setup(
    platforms=['OS-independent'],
    classifiers=classifiers,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['sherry'],
    python_requires='>=3.6',
    **info
)
