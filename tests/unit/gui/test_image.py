# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.gui.image."""

import pytest

from vimiv.gui import image


def test_open_image(tmpimage, qtbot, objregistry):
    scrollable_image = image.ScrollableImage()
    qtbot.addWidget(scrollable_image)
    im = image.Image(parent=scrollable_image)
    qtbot.addWidget(im)
    im.open(tmpimage)
    # TODO assertion


def test_zoom_image(tmpimage, qtbot, objregistry):
    scrollable_image = image.ScrollableImage()
    qtbot.addWidget(scrollable_image)
    im = image.Image(parent=scrollable_image)
    qtbot.addWidget(im)
    im.open(tmpimage)
    w_before = im.pixmap().width()
    im.zoom("in")
    assert im.pixmap().width() > w_before
    im.zoom("out")
    assert im.pixmap().width() == pytest.approx(w_before, rel=2)