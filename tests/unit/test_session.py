#!/usr/bin/env python

"""Tests for `armonik_cli` package."""


from src.armonik_cli.session import hello


def test_hello():
    assert hello() == "Hello, Session!"
