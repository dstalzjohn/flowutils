"""module for tests of url module"""

from flowutils.url import escape_url


def test_escape_url_with_spaces():
    assert escape_url("/path/with spaces/file.pdf") == "/path/with%20spaces/file.pdf"


def test_escape_url_with_tilde():
    assert escape_url("/path/with~tilde/file.pdf") == "/path/with%7Etilde/file.pdf"


def test_escape_url_with_spaces_and_tilde():
    assert (
        escape_url("/path/with spaces/and~tilde.pdf")
        == "/path/with%20spaces/and%7Etilde.pdf"
    )


def test_escape_url_with_other_special_characters():
    assert (
        escape_url("/path/with?query=value&other=123")
        == "/path/with%3Fquery%3Dvalue%26other%3D123"
    )


def test_escape_url_with_unicode():
    assert (
        escape_url("/path/with/ünicode/チャラクター")
        == "/path/with/%C3%BCnicode/%E3%83%81%E3%83%A3%E3%83%A9%E3%82%AF%E3%82%BF%E3%83%BC"
    )


def test_escape_url_no_changes_needed():
    assert (
        escape_url("/normal/path/without/special/chars.pdf")
        == "/normal/path/without/special/chars.pdf"
    )


def test_escape_url_empty_string():
    assert escape_url("") == ""
