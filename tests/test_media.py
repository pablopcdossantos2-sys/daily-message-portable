import pytest
from PIL import Image

from dailymessage import config, media


def test_import_resolve_cleanup(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path / "cfg")
    src = tmp_path / "x.png"
    Image.new("RGB", (4000, 1000), (255, 0, 0)).save(src)
    name = media.import_image(src)
    assert config.IMAGE_NAME_RE.match(name)
    path = media.resolve(name)
    assert path and path.is_file()
    with Image.open(path) as im:
        assert max(im.size) <= media.MAX_SIDE
    assert media.resolve("../evil.png") is None
    other = media.import_image(src)
    media.cleanup({name})
    assert media.resolve(other) is None and media.resolve(name)


def test_rejects_invalid_files(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "config_dir", lambda: tmp_path / "cfg")
    fake = tmp_path / "a.png"
    fake.write_text("não é imagem")
    with pytest.raises(ValueError):
        media.import_image(fake)
    txt = tmp_path / "a.txt"
    txt.write_text("x")
    with pytest.raises(ValueError):
        media.import_image(txt)
