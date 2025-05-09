"""
EasySwitch - Python dictionnary config source loader.
"""

from typing import Dict, Any
from easyswitch.conf.base import BaseConfigSource
from easyswitch.conf import register_source


####
##      DICT CONFIGURATION SOURSE CLASS
#####
@register_source('dict')
class DictConfigSource(BaseConfigSource):
    """Load EasySwitch configurations from a Python dictionnary object."""
    
    def __init__(self, config_dict: Dict[str, Any]):
        self.config_dict = config_dict

    def load(self) -> Dict[str, Any]:
        """Return the config dict."""
        return self.config_dict

    def is_valid(self) -> bool:
        """Always valid if the dictionary exixts."""
        return bool(self.config_dict)