from dailymessage.sizing import BASE_H, BASE_W, estimate_size


def test_empty_and_growth():
    assert estimate_size([]) == (BASE_W, BASE_H)
    short = estimate_size([{"type": "text", "style": "body", "text": "Oi"}])
    long = estimate_size([{"type": "text", "style": "body", "text": "palavra " * 800}])
    assert long[1] > short[1] > BASE_H


def test_image_widens_and_checklist_grows():
    w, h = estimate_size([{"type": "image", "file": "0" * 32 + ".png", "caption": ""}])
    assert w > BASE_W and h > BASE_H
    _, h2 = estimate_size([{"type": "checklist", "title": "", "items": ["a", "b", "c"], "required": True}])
    assert h2 > BASE_H
