# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.runners."""

import pytest

from vimiv.commands import runners


@pytest.mark.parametrize("text", [" ", "\n", " \n", "\t\t", "\n \t"])
def test_text_non_whitespace_with_whitespace(text):
    """Ensure the decorated function is not called with plain whitespace."""

    @runners.text_non_whitespace
    def function(input):
        raise AssertionError("The function should not be called")

    function(text)


@pytest.mark.parametrize("text", [" txt", "\ntxt", " \ntxt", "\ttxt\t", "\n txt\t"])
def test_text_non_whitespace_with_non_whitespace(text, mocker):
    """Ensure the decorated function is called with stripped text."""

    mock = mocker.Mock()

    @runners.text_non_whitespace
    def function(input):
        mock(input)

    function(text)
    assert mock.called_once_with("txt")


@pytest.mark.parametrize("wildcard", ("%", "%m", "%wildcard", "%f"))
@pytest.mark.parametrize("escaped", (True, False))
@pytest.mark.parametrize(
    "text", ("{wildcard} start", "in the {wildcard} middle", "end {wildcard}")
)
def test_expand_wildcard(wildcard, escaped, text):
    text = text.format(wildcard=rf"\{wildcard}" if escaped else wildcard)
    paths = "this", "is", "text"
    result = runners.expand_wildcard(text, wildcard, lambda: paths)

    if escaped:
        expected = text.replace("\\", "")
    else:
        expected = text.replace(wildcard, " ".join(paths))

    assert result == expected


def test_recursive_wildcards():
    """Ensure unescaping of wildcards does not lead to them being matched later."""
    text = r"This has an escaped wildcard \%m"
    expected = "This has an escaped wildcard %m"
    intermediate = runners.expand_wildcard(text, "%m", lambda: "anything")
    result = runners.expand_wildcard(intermediate, "%", lambda: "anything")
    assert result == expected
