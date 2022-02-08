"""A tool to calculate thermodynamic properties via the superposition approximation."""

# Add imports here
from .occuprob import *
from .partitionfunctions import *
from .superpositions import *
from .utils import *
from .io import *

# Handle versioneer
from ._version import get_versions
versions = get_versions()
__version__ = versions['version']
__git_revision__ = versions['full-revisionid']
del get_versions, versions
