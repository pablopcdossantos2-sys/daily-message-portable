from dailymessage import theme


def test_mix_midpoint():
    black, white = ("#000000", "#000000"), ("#FFFFFF", "#FFFFFF")
    assert theme.mix(black, white, 0.5) == ("#808080", "#808080")
    assert theme.mix(black, white, 0) == black
    assert theme.mix(black, white, 1) == white
