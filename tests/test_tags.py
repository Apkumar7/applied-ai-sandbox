"""Tests for the tags field on note dicts."""
import re


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


def test_tags_comma_split(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "B", "tags": "work, urgent"})
    assert app.notes[0]["tags"] == ["work", "urgent"]


def test_tags_whitespace_and_empty_entries_ignored(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "B", "tags": " work , urgent  , ,"})
    assert app.notes[0]["tags"] == ["work", "urgent"]


def test_tags_empty_string_gives_empty_list(client, app):
    app.notes.clear()
    client.post("/notes/new", data={"title": "T", "body": "B", "tags": ""})
    assert app.notes[0]["tags"] == []


def test_tags_render_as_chips(client, app):
    app.notes.clear()
    app.notes.append({"title": "T", "body": "B", "tags": ["work"]})
    r = client.get("/")
    assert b"work" in r.data


def test_filter_bar_deduplicates_tags(client, app):
    app.notes.clear()
    app.notes.append({"title": "A", "body": "x", "tags": ["work", "urgent"]})
    app.notes.append({"title": "B", "body": "y", "tags": ["work"]})
    r = client.get("/")
    body = r.data.decode()
    filter_labels = re.findall(r'class="filter[^"]*"[^>]*>\s*([^<\s][^<]*?)\s*</a>', body)
    filter_tags = [lbl for lbl in filter_labels if lbl != "All"]
    assert sorted(filter_tags) == ["urgent", "work"]


def test_filter_by_tag_hides_non_matching(client, app):
    app.notes.clear()
    app.notes.append({"title": "Work note",     "body": "x", "tags": ["work"]})
    app.notes.append({"title": "Personal note", "body": "y", "tags": ["personal"]})
    r = client.get("/?tag=work")
    body = r.data.decode()
    assert "Work note" in body
    assert "Personal note" not in body


def test_filter_all_shows_every_note(client, app):
    app.notes.clear()
    app.notes.append({"title": "Work note",     "body": "x", "tags": ["work"]})
    app.notes.append({"title": "Personal note", "body": "y", "tags": ["personal"]})
    r = client.get("/")
    body = r.data.decode()
    assert "Work note" in body
    assert "Personal note" in body
