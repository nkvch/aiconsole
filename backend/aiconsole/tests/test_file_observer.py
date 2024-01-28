from pathlib import Path
from unittest.mock import MagicMock

from aiconsole.core.settings.fs.file_observer import FileObserver


def test_start_observer():
    # Create a mock on_changed function
    on_changed_mock = MagicMock()

    # Create a list of file paths to observe
    file_paths = [Path("/path/to/file1.txt"), Path("/path/to/file2.txt")]

    # Create an instance of FileObserver
    file_observer = FileObserver()

    # Start the observer
    file_observer.start(file_paths, on_changed_mock)

    # Assert that the observer is observing the correct file paths
    assert file_observer.observing == file_paths

    # Assert that the observer is started
    assert file_observer._observer and file_observer._observer.is_alive()

    # Stop the observer
    file_observer.stop()

    # Assert that the observer is stopped
    assert not file_observer._observer.is_alive()
    assert file_observer.observing == []
