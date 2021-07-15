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
        'Documentation': 'https://py-mu.github.io/sherry/',
        'Funding': 'https://donate.pypi.org',
        'Source': 'https://github.com/py-mu/sherry',
        'Tracker': 'https://github.com/py-mu/sherry/issues',
    },
    'name': 'sherry-tooltip',
    'version': '1.0.0',
    'description': 'Quickly develop a theme-based qt desktop program',
    'author': '黄大胆',
    'author_email': '1540235670@qq.com',
    'url': 'https://github.com/py-mu/sherry',
    'license': 'Apache',
    'keywords': 'GUI'
}

# 分类信息
classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers'
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: Chinese',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

setup(
    platforms=['OS-independent'],
    classifiers=classifiers,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['QtAwesome>=0.7.0', 'PyQt5>=5.12', 'sherry'],
    python_requires='>=3.6',
    **info
)
