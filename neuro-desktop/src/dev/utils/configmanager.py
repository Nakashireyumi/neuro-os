import shutil
import yaml
from pathlib import Path
from datetime import datetime

from nakuritycore.utils.logging import Logger
from nakuritycore.data.config.logging import LoggingConfig

# Setup logging
logger = Logger(__name__, LoggingConfig(
    level="INFO",
    log_file="config_manager.log"
))

class ConfigManager:
    def __init__(self):
        self.base_path = Path(__file__).parents[2].resolve()
        self.configs = {
            'neuro_desktop': {
                'path': self.base_path.parent / 'src' / 'resources' / 'authentication.yaml',
                'name': "Neuro Desktop's Neuro Backend Connection Settings"
            },
            'neuro_relay': {
                'path': self.base_path.parents[2] / 'neuro-relay' / 'src' / 'resources' / 'authentication.yaml',
                'name': 'Neuro Relay Authentication'
            },
            'windows_api': {
                'path': self.base_path.parents[2] / 'windows-api' / 'src' / 'resources' / 'gui' / 'config' / 'authentication.yaml',
                'name': 'Windows-API Authentication'
            }
        }
        
        # Create backup directory
        self.backup_dir = self.base_path / 'backups'
        self.backup_dir.mkdir(exist_ok=True)
    
    def load_config(self, config_name):
        """Load a configuration file"""
        try:
            config_info = self.configs[config_name]
            with open(config_info['path'], 'r') as f:
                return yaml.safe_load(f), None
        except FileNotFoundError:
            return None, f"Config file not found: {config_info['path']}"
        except yaml.YAMLError as e:
            return None, f"YAML parsing error: {str(e)}"
        except Exception as e:
            return None, f"Error loading config: {str(e)}"
    
    def save_config(self, config_name, data):
        """Save a configuration file with backup"""
        try:
            config_info = self.configs[config_name]
            
            # Create backup before saving
            self._create_backup(config_name)
            
            # Save new config
            with open(config_info['path'], 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved config: {config_name}")
            return True, None
        except Exception as e:
            error_msg = f"Error saving config {config_name}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def _create_backup(self, config_name):
        """Create a backup of the current config"""
        try:
            config_info = self.configs[config_name]
            if config_info['path'].exists():
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                backup_filename = f"{config_name}_{timestamp}.yaml"
                backup_path = self.backup_dir / backup_filename
                shutil.copy2(config_info['path'], backup_path)
                logger.info(f"Created backup: {backup_path}")
        except Exception as e:
            logger.error(f"Failed to create backup for {config_name}: {str(e)}")
    
    def get_all_configs(self):
        """Load all configuration files"""
        configs = {}
        for name, info in self.configs.items():
            data, error = self.load_config(name)
            configs[name] = {
                'data': data,
                'error': error,
                'name': info['name'],
                'path': str(info['path']),
                'exists': info['path'].exists()
            }
        return configs
    
    def validate_config(self, config_name, data):
        """Validate configuration data"""
        validation_rules = {
            'neuro_os': self._validate_neuro_os,
            'neuro_relay': self._validate_neuro_relay,
            'windows_api': self._validate_windows_api
        }
        
        validator = validation_rules.get(config_name)
        if validator:
            return validator(data)
        return True, None
    
    def _validate_neuro_os(self, data):
        """Validate neuro-os config"""
        required_fields = ['relay_connection']
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        relay_conn = data['relay_connection']
        if not isinstance(relay_conn.get('port'), int):
            return False, "relay_connection.port must be an integer"
        
        return True, None
    
    def _validate_neuro_relay(self, data):
        """Validate neuro-relay config"""
        required_sections = ['intermediary', 'nakurity-backend', 'nakurity-client']
        for section in required_sections:
            if section not in data:
                return False, f"Missing required section: {section}"
        
        # Validate port numbers
        for section in required_sections:
            if 'port' in data[section] and not isinstance(data[section]['port'], int):
                return False, f"{section}.port must be an integer"
        
        return True, None
    
    def _validate_windows_api(self, data):
        """Validate windows-api config"""
        if 'port' in data and not isinstance(data['port'], int):
            return False, "port must be an integer"
        
        if 'pause' in data and not isinstance(data['pause'], (int, float)):
            return False, "pause must be a number"
        
        return True, None