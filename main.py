from cli.menu import run_menu
from config.settings import SettingsError, load_settings
from core.logger import configure_logging, get_logger


def main() -> None:
    """Configure application services and run the interactive CLI."""

    configure_logging()
    logger = get_logger(__name__)

    logger.info("Starting Evil Twin Lab")

    try:
        settings = load_settings()

        logger.debug(
            "Active settings: lab_interface=%s, protected_interface=%s",
            settings.lab_interface,
            settings.protected_interface,
        )

        run_menu()

    except SettingsError as exc:
        logger.critical(
            "Could not load application configuration: %s",
            exc,
        )

    except KeyboardInterrupt:
        logger.warning("Application interrupted by user")

    except Exception:
        logger.exception("Unexpected application error")
        raise

    finally:
        logger.info("Evil Twin Lab stopped")


if __name__ == "__main__":
    main()