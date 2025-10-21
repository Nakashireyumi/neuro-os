"""
Configuration loader utility for debug and trace settings
Loads config.yaml and applies settings across all modules
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

class ConfigLoader:
    """Loads and manages configuration settings"""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Default to config.yaml in the same directory as this file
            config_path = Path(__file__).parent.parent / "config.yaml"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config if config else {}
        except FileNotFoundError:
            print(f"Config file not found: {self.config_path}")
            return self._default_config()
        except yaml.YAMLError as e:
            print(f"Error parsing config file: {e}")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration if file is missing or invalid"""
        return {
            "debug": {
                "enabled": True,
                "trace": {
                    "enabled": False,
                    "verbose": False
                }
            }
        }
    
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        return self.config.get("debug", {}).get("enabled", False)
    
    def is_trace_enabled(self) -> bool:
        """Check if tracing is enabled"""
        return (
            self.is_debug_enabled() and 
            self.config.get("debug", {}).get("trace", {}).get("enabled", False)
        )
    
    def get_trace_config(self) -> Dict[str, Any]:
        """Get trace configuration"""
        return self.config.get("debug", {}).get("trace", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get("debug", {}).get("logging", {})
    
    def get_connection_config(self) -> Dict[str, Any]:
        """Get connection configuration"""
        return self.config.get("connection", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Get performance configuration"""
        return self.config.get("performance", {})
    
    def setup_logging(self) -> None:
        """Setup logging based on configuration"""
        log_config = self.get_logging_config()
        
        level_str = log_config.get("level", "INFO")
        level = getattr(logging, level_str.upper(), logging.INFO)
        
        # Setup logging format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup console handler
        if log_config.get("console", True):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
        
        # Setup file handler
        log_file = log_config.get("file")
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logging.getLogger().addHandler(file_handler)
        
        logging.getLogger().setLevel(level)
    
    def apply_trace_config(self, trace_func):
        """Apply trace configuration to the trace function"""
        if not self.is_trace_enabled():
            # Disable tracing
            sys.settrace(None)
            return
        
        trace_config = self.get_trace_config()
        
        # Apply configuration to trace function if it has these attributes
        if hasattr(trace_func, 'config'):
            trace_func.config.update(trace_config)
        
        # Set the trace function
        sys.settrace(trace_func)
    
    def get_retry_config(self) -> Dict[str, Any]:
        """Get retry configuration for connections"""
        return self.config.get("connection", {}).get("retry", {
            "max_attempts": 10,
            "initial_delay": 5,
            "max_delay": 60,
            "backoff_multiplier": 1.5
        })


# Global configuration instance
_config_loader = None

def get_config_loader(config_path: Optional[str] = None) -> ConfigLoader:
    """Get or create global configuration loader"""
    global _config_loader
    if _config_loader is None or config_path is not None:
        _config_loader = ConfigLoader(config_path)
    return _config_loader

def is_debug_enabled() -> bool:
    """Quick check if debug mode is enabled"""
    return get_config_loader().is_debug_enabled()

def is_trace_enabled() -> bool:
    """Quick check if tracing is enabled"""
    return get_config_loader().is_trace_enabled()

def setup_logging() -> None:
    """Setup logging from configuration"""
    get_config_loader().setup_logging()

def apply_trace_config(trace_func) -> None:
    """Apply trace configuration"""
    get_config_loader().apply_trace_config(trace_func)