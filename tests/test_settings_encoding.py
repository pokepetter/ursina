import builtins
import os

from ursina import application

TITLE = 'Łukasz ✨'


def _open_with_cp1252_default(original_open):
    # Simulate a Windows locale where open() does not default to UTF-8.
    def open_(file, mode='r', buffering=-1, encoding=None, *args, **kwargs):
        if 'b' not in mode and encoding is None:
            encoding = 'cp1252'
        return original_open(file, mode, buffering, encoding, *args, **kwargs)
    return open_


def _load(tmp_path, monkeypatch, data):
    path = tmp_path / 'ursina_settings.py'
    path.write_bytes(data)
    monkeypatch.delenv('URSINA_SETTINGS_TEST', raising=False)
    monkeypatch.setattr(builtins, 'open', _open_with_cp1252_default(builtins.open))
    application.load_settings(path)
    return os.environ.get('URSINA_SETTINGS_TEST')


def test_settings_file_is_read_as_utf8(tmp_path, monkeypatch):
    # Python source files are UTF-8 by default, so ursina_settings.py must not be read with the locale encoding.
    code = f"import os\nos.environ['URSINA_SETTINGS_TEST'] = '{TITLE}'\n"
    assert _load(tmp_path, monkeypatch, code.encode('utf-8')) == TITLE


def test_settings_file_with_utf8_bom(tmp_path, monkeypatch):
    # Some Windows editors save UTF-8 files with a byte order mark.
    code = f"import os\nos.environ['URSINA_SETTINGS_TEST'] = '{TITLE}'\n"
    assert _load(tmp_path, monkeypatch, b'\xef\xbb\xbf' + code.encode('utf-8')) == TITLE
