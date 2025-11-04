# src/plugins/__init__.py
"""Neuro Desktop Plugins System"""

from .plugin_manager import (
    PluginManager,
    PluginManifest,
    Plugin,
    PluginContext,
    get_plugin_manager
)

__all__ = [
    'PluginManager',
    'PluginManifest',
    'Plugin',
    'PluginContext',
    'get_plugin_manager'
]# Plugins package for Neuro-OS
