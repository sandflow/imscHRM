#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2021, Pearl TV LLC
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Unit tests for the DocumentSequence class"""

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
from fractions import Fraction

from imschrm.doc_sequence import iter_isd
from imschrm.cli import LocalFileSequence, SingleLocalFile
import imschrm.hrm

class DummyErrorHandler:

  def __init__(self):
    self.error_times = []

  def info(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: imschrm.hrm.ISDStatistics):
    pass

  def warn(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: imschrm.hrm.ISDStatistics):
    pass

  def error(self, _msg: str, _doc_index: int, time_offset: Fraction, _available_time: Fraction, _stats: imschrm.hrm.ISDStatistics):
    self.error_times.append(time_offset)

  def debug(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: imschrm.hrm.ISDStatistics):
    pass

class ValidateTests(unittest.TestCase):

  def test_local_file_sequence(self):

    ds = LocalFileSequence("src/test/resources/ttml/sequence001/manifest.json")

    isds = tuple(iter_isd(ds))

    self.assertEqual(len(isds), 6)

    self.assertEqual(isds[0][0], 0.5)
    self.assertEqual(isds[1][0], 1)
    self.assertEqual(isds[2][0], 2)
    self.assertEqual(isds[3], (3, None))
    self.assertEqual(isds[4][0], 5)
    self.assertEqual(isds[5][0], 6)

  def test_fail_1(self):

    ev = DummyErrorHandler()

    doc_sequence = SingleLocalFile("src/test/resources/ttml/fail001.ttml")

    imschrm.hrm.validate(imschrm.doc_sequence.iter_isd(doc_sequence), ev)

    self.assertSequenceEqual(ev.error_times, (Fraction(1, 10),))

  def test_fail_2(self):

    ev = DummyErrorHandler()

    doc_sequence = LocalFileSequence("src/test/resources/ttml/fail002/manifest.json")

    imschrm.hrm.validate(imschrm.doc_sequence.iter_isd(doc_sequence), ev)

    self.assertSequenceEqual(ev.error_times, (1,))

if __name__ == '__main__':
  unittest.main()
