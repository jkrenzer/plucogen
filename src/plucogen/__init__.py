_module_name = __name__
from . import api, logging

log = logging.getLogger(__name__)

try:
    log.debug("Startup logging begins")
    from . import api, cli, consumers
except ImportError as e:
    logging.start()
    log.exception("Unable to import all modules. Emergency stop.")
finally:
    logging.shutdown()


def _is_defined() -> bool:
    return True
