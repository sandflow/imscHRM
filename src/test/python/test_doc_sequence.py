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

from imschrm.doc_sequence import iter_isd

TTML_DOC_1 = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"  xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="0s" end="1s">0-1</p>
      <p begin="1s" end="2s">1-2</p>
      <p begin="4s" end="5s">4-5</p>
    </div>
  </body>
</tt>'''

TTML_DOC_2 = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"  xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="2s" end="3s">2-3</p>
      <p begin="5s" end="6s">5-6</p>
    </div>
  </body>
</tt>'''

TTML_DOC_3 = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"  xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="5s" end="6s">5-6</p>
    </div>
  </body>
</tt>'''

class DocumentSequenceTests(unittest.TestCase):

  def test_iter_isd_1(self):

    isds = tuple(iter_isd(
      [
        (0, 2, TTML_DOC_1),
        (6, None, TTML_DOC_2)
      ]
    ))

    self.assertEqual(len(isds), 4)

    self.assertEqual(isds[0][0], 0)
    self.assertEqual(isds[1][0], 1)
    self.assertEqual(isds[2][0], 2)
    self.assertEqual(isds[3][0], 6)

  def test_iter_isd_2(self):

    isds = tuple(iter_isd(
      [
        (0.5, 3, TTML_DOC_1),
        (5, None, TTML_DOC_2)
      ]
    ))

    self.assertEqual(len(isds), 6)

    self.assertEqual(isds[0][0], 0.5)
    self.assertEqual(isds[1][0], 1)
    self.assertEqual(isds[2][0], 2)
    self.assertEqual(isds[3], (3, None))
    self.assertEqual(isds[4][0], 5)
    self.assertEqual(isds[5][0], 6)

  def test_iter_isd_3(self):


    isds = tuple(iter_isd(
      [
        (0, 5, TTML_DOC_1),
        (5, 6, TTML_DOC_3)
      ]
    ))

    self.assertEqual(len(isds), 5)

    self.assertEqual(isds[0][0], 0)
    self.assertEqual(isds[1][0], 1)
    self.assertEqual(isds[2][0], 2)
    self.assertEqual(isds[3][0], 4)
    self.assertEqual(isds[4][0], 5)

if __name__ == '__main__':
  unittest.main()
