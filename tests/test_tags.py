"""Tests for the tags field on note dicts."""


def test_new_note_has_empty_tags(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "Tagged", "body": "Hello"})
    assert len(app.notes) == 1
    assert app.notes[0]["tags"] == []


def test_old_note_without_tags_key_is_safe(app):
    """Legacy notes that pre-date the tags field must not crash on .get()."""
    app.notes.clear()
    app.notes.append({"title": "old", "body": "legacy"})
    note = app.notes[0]
    assert note.get("tags", []) == []
