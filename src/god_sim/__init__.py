"""GOD simulation package."""

from .config import WorldConfig
from .engine.sim import run_simulation

__all__ = ["WorldConfig", "run_simulation"]

