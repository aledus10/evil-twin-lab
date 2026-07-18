import logging
import unittest

from core.logger import SUCCESS_LEVEL, configure_logging, get_logger


class LoggerTests(unittest.TestCase):
    def test_success_uses_custom_level_and_deferred_arguments(self):
        logger = get_logger("tests.logger.success")

        with self.assertLogs(logger, level=SUCCESS_LEVEL) as captured:
            logger.success("Found %d networks", 3)

        self.assertEqual(captured.output, ["SUCCESS:tests.logger.success:Found 3 networks"])

    def test_configuration_is_idempotent(self):
        root_logger = configure_logging()
        initial_handlers = [
            handler
            for handler in root_logger.handlers
            if getattr(handler, "_evil_twin_lab_handler", False)
        ]

        configure_logging()
        repeated_handlers = [
            handler
            for handler in root_logger.handlers
            if getattr(handler, "_evil_twin_lab_handler", False)
        ]

        self.assertEqual(len(initial_handlers), 2)
        self.assertEqual(len(repeated_handlers), 2)
        self.assertTrue(any(handler.level == logging.INFO for handler in repeated_handlers))
        self.assertTrue(any(handler.level == logging.DEBUG for handler in repeated_handlers))


if __name__ == "__main__":
    unittest.main()
