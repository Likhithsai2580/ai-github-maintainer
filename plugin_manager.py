import importlib
import os
import logging

class PluginManager:
    def __init__(self, config):
        self.plugins = []
        self.load_plugins(config['plugins'])

    def load_plugins(self, plugin_configs):
        for plugin_config in plugin_configs:
            if plugin_config['enabled']:
                try:
                    module = importlib.import_module(f"plugins.{plugin_config['name']}")
                    plugin = module.Plugin()
                    self.plugins.append(plugin)
                    logging.info(f"Loaded plugin: {plugin_config['name']}")
                except Exception as e:
                    logging.error(f"Error loading plugin {plugin_config['name']}: {str(e)}")

    def run_plugins(self, repo, branch):
        results = []
        for plugin in self.plugins:
            try:
                result = plugin.run(repo, branch)
                results.append(result)
            except Exception as e:
                logging.error(f"Error running plugin {plugin.__class__.__name__}: {str(e)}")
        return results