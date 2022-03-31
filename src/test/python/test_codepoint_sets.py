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

"""Unit tests for the HRM validator"""

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

import unittest

from imschrm.codepoint_sets import GCPY_12, RENGI_06

class CodepointSets(unittest.TestCase):

  def test_gcpy_12(self):
    self.assertIn(ord("*"), GCPY_12) # Common
    self.assertIn(ord("a"), GCPY_12) # Latin
    self.assertIn(ord("͵"), GCPY_12) # Greek
    self.assertIn(ord("҂"), GCPY_12) # Cyrillic
    self.assertIn(ord("א"), GCPY_12) # Hebrew
    self.assertIn(ord("א"), GCPY_12) # Hebrew

    self.assertNotIn(ord("々"), GCPY_12) # Han

  def test_rengi_06(self):
    self.assertIn(ord("々"), RENGI_06) # Han
    self.assertIn(ord("ァ"), RENGI_06) # Katakana
    self.assertIn(ord("ぁ"), RENGI_06) # Hiragana
    self.assertIn(ord("ㄅ"), RENGI_06) # Bopomofo
    self.assertIn(ord("ᄀ"), RENGI_06) # Hangul

    self.assertNotIn(ord("*"), RENGI_06) # Common

if __name__ == '__main__':
  unittest.main()
