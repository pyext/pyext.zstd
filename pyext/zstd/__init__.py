from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from ._zstd import *   # noqa: F401,F403
