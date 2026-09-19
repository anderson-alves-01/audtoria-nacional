from sirta_api.domain.notifications import NOTIFICATIONS_VERSION, build_notifications_page


def test_notifications_page_is_empty_and_send_disabled() -> None:
    assert NOTIFICATIONS_VERSION.startswith("notifications-technical-")
    page = build_notifications_page()
    assert page["binding"] is False
    assert page["operational"] is False
    assert page["homologated"] is False
    assert page["commandsDisabled"] is True
    assert page["sendEnabled"] is False
    assert page["createsTaxCredit"] is False
    assert page["items"] == []
    assert page["total"] == 0
    assert page["g5Status"] == "BLOCKED"
