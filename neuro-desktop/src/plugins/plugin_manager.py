# src/plugins/plugin_manager.py
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from pathlib import Path
import importlib.util
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class PluginManifest:
    """Plugin metadata"""
    id: str
    name: str
    version: str
    description: str
    author: str
    entry_point: str = "main.py"
    permissions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    neuro_integration: bool = False
    enabled: bool = True
    
    @classmethod
    def from_file(cls, manifest_path: Path) -> 'PluginManifest':
        """Load manifest from plugin.json"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'entry_point': self.entry_point,
            'permissions': self.permissions,
            'dependencies': self.dependencies,
            'neuro_integration': self.neuro_integration,
            'enabled': self.enabled
        }

class Plugin:
    """Base plugin class"""
    def __init__(self, manifest: PluginManifest, module: Any):
        self.manifest = manifest
        self.module = module
        self.instance = None
    
    async def activate(self, context: 'PluginContext'):
        """Activate the plugin"""
        if hasattr(self.module, 'activate'):
            self.instance = await self.module.activate(context)
            logger.info(f"Plugin activated: {self.manifest.name}")
        else:
            raise AttributeError(f"Plugin {self.manifest.id} missing activate() function")
    
    async def deactivate(self):
        """Deactivate the plugin"""
        if self.instance and hasattr(self.instance, 'deactivate'):
            await self.instance.deactivate()
            logger.info(f"Plugin deactivated: {self.manifest.name}")

class PluginContext:
    """Context provided to plugins"""
    def __init__(self, plugin_manager: 'PluginManager'):
        self.plugin_manager = plugin_manager
        self.hooks: Dict[str, List[Callable]] = {}
    
    def register_hook(self, hook_name: str, callback: Callable):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
        logger.debug(f"Hook registered: {hook_name}")
    
    async def trigger_hook(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a hook"""
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(*args, **kwargs)
                    else:
                        callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook {hook_name} callback error: {e}")

class PluginManager:
    """Central plugin management system"""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        self.loaded_plugins: Dict[str, Plugin] = {}
        self.context = PluginContext(self)
        
        # Plugin state file
        self.state_file = self.plugins_dir / ".plugin_state.json"
        self.load_state()
    
    def load_state(self):
        """Load plugin enabled/disabled state"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                self.plugin_state = json.load(f)
        else:
            self.plugin_state = {}
    
    def save_state(self):
        """Save plugin state"""
        with open(self.state_file, 'w') as f:
            json.dump(self.plugin_state, f, indent=2)
    
    async def discover_plugins(self) -> List[PluginManifest]:
        """Scan plugins directory for valid plugins"""
        plugins = []
        
        if not self.plugins_dir.exists():
            return plugins
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
                
            manifest_path = plugin_dir / "plugin.json"
            if manifest_path.exists():
                try:
                    manifest = PluginManifest.from_file(manifest_path)
                    
                    # Apply saved state
                    if manifest.id in self.plugin_state:
                        manifest.enabled = self.plugin_state[manifest.id].get('enabled', True)
                    
                    plugins.append(manifest)
                except Exception as e:
                    logger.error(f"Failed to load plugin {plugin_dir.name}: {e}")
        
        return plugins
    
    async def load_plugin(self, plugin_id: str) -> bool:
        """Load and initialize a plugin"""
        try:
            # Find plugin directory
            plugin_dir = self.plugins_dir / plugin_id
            if not plugin_dir.exists():
                logger.error(f"Plugin directory not found: {plugin_id}")
                return False
            
            manifest_path = plugin_dir / "plugin.json"
            manifest = PluginManifest.from_file(manifest_path)
            
            # Check dependencies
            if not self._check_dependencies(manifest):
                logger.error(f"Plugin {plugin_id} has unmet dependencies")
                return False
            
            # Load the plugin module
            entry_path = plugin_dir / manifest.entry_point
            if not entry_path.exists():
                logger.error(f"Entry point not found: {entry_path}")
                return False
            
            spec = importlib.util.spec_from_file_location(plugin_id, entry_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Create plugin instance
            plugin = Plugin(manifest, module)
            await plugin.activate(self.context)
            
            self.loaded_plugins[plugin_id] = plugin
            
            # Update state
            self.plugin_state[plugin_id] = {'enabled': True}
            self.save_state()
            
            logger.info(f"Plugin loaded: {manifest.name} v{manifest.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self.loaded_plugins:
            return False
        
        try:
            plugin = self.loaded_plugins[plugin_id]
            await plugin.deactivate()
            del self.loaded_plugins[plugin_id]
            
            # Update state
            if plugin_id in self.plugin_state:
                self.plugin_state[plugin_id]['enabled'] = False
                self.save_state()
            
            logger.info(f"Plugin unloaded: {plugin.manifest.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_id}: {e}")
            return False
    
    def _check_dependencies(self, manifest: PluginManifest) -> bool:
        """Check if plugin dependencies are met"""
        for dep in manifest.dependencies:
            if dep not in self.loaded_plugins:
                return False
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get a loaded plugin by ID"""
        return self.loaded_plugins.get(plugin_id)
    
    async def load_all_enabled(self):
        """Load all enabled plugins"""
        manifests = await self.discover_plugins()
        
        for manifest in manifests:
            if manifest.enabled and manifest.id not in self.loaded_plugins:
                await self.load_plugin(manifest.id)

# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None

def get_plugin_manager(plugins_dir: Optional[Path] = None) -> PluginManager:
    """Get or create global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        if plugins_dir is None:
            # Default to PROJECT_ROOT/plugins
            from pathlib import Path
            plugins_dir = Path(__file__).resolve().parents[3] / "plugins"
        _plugin_manager = PluginManager(plugins_dir)
    return _plugin_manager
