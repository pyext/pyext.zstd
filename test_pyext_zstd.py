#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import pyext_zstd

def test_pyext_zstd():
    count = pyext_zstd.info("test")
    assert count >= 0
