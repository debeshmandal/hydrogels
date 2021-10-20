from .utils.system import System
from .utils.topology import Topology

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
