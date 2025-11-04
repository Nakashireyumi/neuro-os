# plugins/example-plugin/main.py
import logging

logger = logging.getLogger(__name__)

class ExamplePlugin:
    """Example plugin class"""
    
    def __init__(self, context):
        self.context = context
        logger.info("Example Plugin initialized")
    
    async def on_neuro_action(self, action):
        """Handle Neuro actions"""
        logger.info(f"Neuro action received: {action}")
    
    async def deactivate(self):
        """Cleanup when plugin is deactivated"""
        logger.info("Example Plugin deactivated")

async def activate(context):
    """Plugin entry point"""
    plugin = ExamplePlugin(context)
    
    # Register hooks
    context.register_hook('on_action', plugin.on_neuro_action)
    
    return plugin
