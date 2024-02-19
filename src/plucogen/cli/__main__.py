from plucogen import logging

from .parser import parse_args

log = logging.getLogger(__name__)


def main(args=None):
    options = parse_args(args)

    # Set loglevel
    log_level = logging.log_levels[options.log_level.lower()]
    logging.basicConfig(level=log_level)
    log.info("Started logging. Messages above where buffered since program startup.")

    # Try to execute user command
    try:
        return options.func(options)
    except KeyboardInterrupt:  # pragma: no cover
        log.info("Keyboard interrupt issued. Abort.")
        return 0
    except:  # pragma: no cover
        log.exception("Exception occured!")
        return 1


if __name__ == "__main__":  # pragma: no cover
    import sys

    sys.exit(main(sys.argv[1:]))
