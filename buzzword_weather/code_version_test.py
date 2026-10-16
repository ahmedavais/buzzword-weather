from pathlib import Path

from buzzword_weather.code_version import code_version


def write(folder: Path, name: str, source: str) -> None:
    (folder / name).write_text(source)


def test_gives_the_same_version_for_the_same_source(tmp_path):
    write(tmp_path, "spans.py", "ALL_TIME = 1")

    assert code_version(tmp_path) == code_version(tmp_path)


def test_changes_when_a_file_changes(tmp_path):
    write(tmp_path, "spans.py", "SINCE_2007 = 1")
    before = code_version(tmp_path)

    write(tmp_path, "spans.py", "ALL_TIME = 1")

    assert code_version(tmp_path) != before


def test_changes_when_a_file_is_added(tmp_path):
    write(tmp_path, "spans.py", "ALL_TIME = 1")
    before = code_version(tmp_path)

    write(tmp_path, "__init__.py", "")

    assert code_version(tmp_path) != before


def test_changes_when_a_file_is_renamed(tmp_path):
    write(tmp_path, "spans.py", "ALL_TIME = 1")
    before = code_version(tmp_path)

    (tmp_path / "spans.py").rename(tmp_path / "history.py")

    assert code_version(tmp_path) != before


def test_ignores_compiled_caches(tmp_path):
    write(tmp_path, "spans.py", "ALL_TIME = 1")
    before = code_version(tmp_path)

    (tmp_path / "__pycache__").mkdir()
    write(tmp_path / "__pycache__", "spans.cpython-312.py", "compiled")

    assert code_version(tmp_path) == before
