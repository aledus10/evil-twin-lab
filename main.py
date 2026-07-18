from core.logger import configure_logging, get_logger
from cli.menu import run_menu


def main() -> None:
    """Configure application services and run the interactive CLI."""
    configure_logging()
    logger = get_logger(__name__)
    logger.info("Starting Evil Twin Lab")

    try:
        run_menu()
    except KeyboardInterrupt:
        logger.warning("Application interrupted by user")
    except Exception:
        logger.exception("Unexpected application error")
        raise
    finally:
        logger.info("Evil Twin Lab stopped")


if __name__ == "__main__":
    main()
