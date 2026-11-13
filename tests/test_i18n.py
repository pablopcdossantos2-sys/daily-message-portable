from dailymessage.i18n import STRINGS, Translator


def test_same_keys_in_all_languages():
    assert set(STRINGS["pt-BR"]) == set(STRINGS["en"])


def test_format_and_fallback():
    assert "3" in Translator("pt-BR").t("time.range", min=3, max=600)
    assert Translator("xx").lang == "en"
    assert Translator("en").t("chave.inexistente") == "chave.inexistente"
