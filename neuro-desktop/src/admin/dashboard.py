# src/admin/dashboard.py
import yaml
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'neuro-os-admin-dashboard-secret-key'

from nakuritycore.utils.logging import Logger
from nakuritycore.data.config.logging import LoggingConfig

# Setup logging
logger = Logger(__name__, LoggingConfig(
    level="INFO",
    log_file="admin_dashboard.log"
))

from ..dev.utils.configmanager import ConfigManager
config_manager = ConfigManager()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    configs = config_manager.get_all_configs()
    return render_template('dashboard.html', configs=configs)

@app.route('/config/<config_name>')
def view_config(config_name):
    """View and edit a specific configuration"""
    if config_name not in config_manager.configs:
        flash(f"Unknown configuration: {config_name}", 'error')
        return redirect(url_for('dashboard'))
    
    data, error = config_manager.load_config(config_name)
    config_info = config_manager.configs[config_name]
    
    return render_template('config_editor.html', 
                         config_name=config_name,
                         config_data=data,
                         config_info=config_info,
                         error=error)

@app.route('/api/config/<config_name>', methods=['GET'])
def get_config_api(config_name):
    """API endpoint to get configuration data"""
    data, error = config_manager.load_config(config_name)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(data)

@app.route('/api/config/<config_name>', methods=['POST'])
def save_config_api(config_name):
    """API endpoint to save configuration data"""
    try:
        data = request.get_json()
        
        # Validate the configuration
        is_valid, error = config_manager.validate_config(config_name, data)
        if not is_valid:
            return jsonify({'error': f"Validation failed: {error}"}), 400
        
        # Save the configuration
        success, error = config_manager.save_config(config_name, data)
        if not success:
            return jsonify({'error': error}), 500
        
        return jsonify({'success': True, 'message': f'Configuration {config_name} saved successfully'})
    
    except Exception as e:
        logger.error(f"Error in save_config_api: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/save_config/<config_name>', methods=['POST'])
def save_config_form(config_name):
    """Handle form submission for configuration saving"""
    try:
        # Get the YAML data from the form
        yaml_content = request.form.get('yaml_content')
        
        # Parse the YAML
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            flash(f"YAML parsing error: {str(e)}", 'error')
            return redirect(url_for('view_config', config_name=config_name))
        
        # Validate the configuration
        is_valid, error = config_manager.validate_config(config_name, data)
        if not is_valid:
            flash(f"Validation failed: {error}", 'error')
            return redirect(url_for('view_config', config_name=config_name))
        
        # Save the configuration
        success, error = config_manager.save_config(config_name, data)
        if success:
            flash(f'Configuration {config_name} saved successfully!', 'success')
        else:
            flash(f'Failed to save configuration: {error}', 'error')
        
        return redirect(url_for('view_config', config_name=config_name))
    
    except Exception as e:
        logger.error(f"Error in save_config_form: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('view_config', config_name=config_name))

@app.route('/api/sync_tokens', methods=['POST'])
def sync_tokens():
    """Sync authentication tokens across all configurations"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        # Update tokens in all configurations
        results = {}
        
        # Update neuro-os
        neuro_os_data, error = config_manager.load_config('neuro_os')
        if neuro_os_data and not error:
            neuro_os_data['relay_connection']['auth_token'] = token
            success, error = config_manager.save_config('neuro_os', neuro_os_data)
            results['neuro_os'] = {'success': success, 'error': error}
        else:
            results['neuro_os'] = {'success': False, 'error': error}
        
        # Update neuro-relay
        neuro_relay_data, error = config_manager.load_config('neuro_relay')
        if neuro_relay_data and not error:
            neuro_relay_data['intermediary']['auth_token'] = token
            neuro_relay_data['dependency-authentication']['neuro-os']['auth_token'] = token
            success, error = config_manager.save_config('neuro_relay', neuro_relay_data)
            results['neuro_relay'] = {'success': success, 'error': error}
        else:
            results['neuro_relay'] = {'success': False, 'error': error}
        
        # Update windows-api
        windows_api_data, error = config_manager.load_config('windows_api')
        if windows_api_data and not error:
            windows_api_data['neuro_relay']['auth_token'] = token
            success, error = config_manager.save_config('windows_api', windows_api_data)
            results['windows_api'] = {'success': success, 'error': error}
        else:
            results['windows_api'] = {'success': False, 'error': error}
        
        return jsonify({
            'success': all(r.get('success', False) for r in results.values()),
            'results': results,
            'message': 'Token synchronization completed'
        })
    
    except Exception as e:
        logger.error(f"Error in sync_tokens: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/backups')
def list_backups():
    """List all available backup files"""
    try:
        backups = []
        if config_manager.backup_dir.exists():
            for backup_file in config_manager.backup_dir.glob('*.yaml'):
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)
        return jsonify(backups)
    
    except Exception as e:
        logger.error(f"Error listing backups: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add to imports
from ..plugins import get_plugin_manager

# Initialize plugin manager
plugin_manager = get_plugin_manager()

@app.route('/plugins')
def plugins_page():
    """Plugins management page"""
    return render_template('plugins.html')

@app.route('/api/plugins', methods=['GET'])
async def list_plugins_api():
    """API: List all plugins"""
    try:
        manifests = await plugin_manager.discover_plugins()
        plugins_data = []
        
        for manifest in manifests:
            plugins_data.append({
                **manifest.to_dict(),
                'loaded': manifest.id in plugin_manager.loaded_plugins
            })
        
        return jsonify({
            'success': True,
            'plugins': plugins_data
        })
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/plugins/<plugin_id>/enable', methods=['POST'])
async def enable_plugin_api(plugin_id: str):
    """API: Enable/load a plugin"""
    try:
        success = await plugin_manager.load_plugin(plugin_id)
        if success:
            return jsonify({'success': True, 'message': f'Plugin {plugin_id} enabled'})
        else:
            return jsonify({'success': False, 'error': 'Failed to load plugin'}), 400
    except Exception as e:
        logger.error(f"Error enabling plugin {plugin_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/plugins/<plugin_id>/disable', methods=['POST'])
async def disable_plugin_api(plugin_id: str):
    """API: Disable/unload a plugin"""
    try:
        success = await plugin_manager.unload_plugin(plugin_id)
        if success:
            return jsonify({'success': True, 'message': f'Plugin {plugin_id} disabled'})
        else:
            return jsonify({'success': False, 'error': 'Plugin not loaded'}), 400
    except Exception as e:
        logger.error(f"Error disabling plugin {plugin_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Add new routes for Neuro control settings

@app.route('/neuro-control')
def neuro_control_page():
    """Neuro control settings page"""
    # Load Neuro control config
    neuro_config = load_neuro_control_config()
    return render_template('neuro_control.html', config=neuro_config)

@app.route('/api/neuro-control', methods=['GET'])
def get_neuro_control_api():
    """API: Get Neuro control settings"""
    config = load_neuro_control_config()
    return jsonify(config)

@app.route('/api/neuro-control', methods=['POST'])
def save_neuro_control_api():
    """API: Save Neuro control settings"""
    try:
        data = request.get_json()
        save_neuro_control_config(data)
        return jsonify({'success': True, 'message': 'Settings saved'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def load_neuro_control_config():
    """Load Neuro control configuration"""
    config_path = Path(__file__).parents[2] / 'src' / 'resources' / 'neuro_control.yaml'
    if config_path.exists():
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    return {
        'enabled': False,
        'theme': 'Dark',
        'autostart': False,
        'allowed_actions': []
    }

def save_neuro_control_config(data):
    """Save Neuro control configuration"""
    config_path = Path(__file__).parents[2] / 'src' / 'resources' / 'neuro_control.yaml'
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)

if __name__ == '__main__':
    # Create templates directory and basic templates if they don't exist
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Run the Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
