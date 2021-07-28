# coding=utf-8
"""
    create by pymu
    on 2021/7/15
    at 17:27
"""
try:
    from sherry_tooltip.injector import TooltipAgent
except ImportError:
    from sherry_tooltip.primary_hook import TooltipAgent

version = (1, 0, 9)
__all__ = ('TooltipAgent', 'version')
