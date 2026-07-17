from pathlib import Path

from core.logging import LoggingConfig, LoggingManager


def test_logging_manager_creates_logger(tmp_path: Path) -> None:
    log_file = tmp_path / "subforge.log"
    manager = LoggingManager(LoggingConfig(level="DEBUG", log_file=log_file))
    logger = manager.configure("subforge.tests")

    logger.info("hello")

    assert logger.name == "subforge.tests"
    assert log_file.exists()

