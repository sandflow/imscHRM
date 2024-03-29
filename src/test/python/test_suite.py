#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2023, Sandflow Consulting LLC
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

"""HRM Test Suite"""

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
import os.path
from fractions import Fraction

import imschrm.hrm
import imschrm.doc_sequence

class EventHandler(imschrm.hrm.EventHandler):

  def __init__(self):
    self.failed = False

  def error(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: imschrm.hrm.ISDStatistics):
    self.failed = True

class HRMTestSuite(unittest.TestCase):

  def test_fail_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/test-suite/fail"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            with open(os.path.join(root, filename), "r", encoding="utf-8") as f:
              ev = EventHandler()
              imschrm.hrm.validate(imschrm.doc_sequence.iter_isd([(0, None, f.read())]), ev, 0)
              self.assertTrue(ev.failed)

  def test_pass_test_suite(self):
    for root, _subdirs, files in os.walk("src/test/resources/ttml/test-suite/pass"):
      for filename in files:
        (name, ext) = os.path.splitext(filename)
        if ext == ".ttml":
          with self.subTest(name):
            with open(os.path.join(root, filename), "r", encoding="utf-8") as f:
              ev = EventHandler()
              imschrm.hrm.validate(imschrm.doc_sequence.iter_isd([(0, None, f.read())]), ev, 0)
              self.assertFalse(ev.failed)

if __name__ == '__main__':
  unittest.main()
