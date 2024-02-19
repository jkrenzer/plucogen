import sys
from uu import Error

from .cli.__main__ import main
from . import logging

log = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except Error as e:
        logging.start()
        log.exception("Error encoauntered during execution.")
    finally:
        logging.shutdown()
