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

"""Generates a Python source file that contains sets of Unicode codepoints used
by the IMSC HRM, e.g., to determine the value of GCpy at IMSC, 10.5"""

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

import argparse
import re

TEMPLATE="""#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'''Sets of Unicode codepoints used by the IMSC HRM.'''

# Generated from the Unicode Character Database (http://www.unicode.org/Public/UNIDATA/Scripts.txt)
# Version: {version}
# Date: {date}

# Normalized glyph copy performance factor (GCpy) for Latin, Greek, Cyrillic, Hebrew or Common
GCPY_12 = set(
(
{codepoints_GCPY_12}
)
)

# Text rendering performance factor Ren(Gi) for Han, Katakana, Hiragana, Bopomofo or Hangul scripts
RENGI_06 = set(
(
{codepoints_RENGI_06}
)
)
"""

SCRIPT_LINE_PATTERN = re.compile(r"(?P<start>[a-fA-F0-9]{4})(?:\.\.(?P<end>[a-fA-F0-9]{4}))?\s+;\s+(?P<script>\w*)")

VERSION_LINE_PATTERN = re.compile(r"^#\s+(.+)$")

DATE_LINE_PATTERN = re.compile(r"^#\s*Date:\s*(.+)$")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Generates the _codepoints_sets.py file')
  parser.add_argument('scripts_file', type=str, help='Path to the input unicode Scripts.txt file')
  parser.add_argument('py_file', type=str, help='Path to the generated Python source file')

  args = parser.parse_args()

  gcpy_12 = set()

  rengi_06 = set()

  with open(args.scripts_file, encoding="latin-1") as f:

    file_version = VERSION_LINE_PATTERN.match(f.readline()).group(1)

    file_date = DATE_LINE_PATTERN.match(f.readline()).group(1)

    for line in f:
      m = SCRIPT_LINE_PATTERN.match(line)

      if m is None:
        continue

      script = m.group("script").lower()

      if script in ("common", "latin", "greek", "hebrew", "cyrillic"):
        cp_group = gcpy_12
      elif script in ("han", "katakana", "hiragana", "bopomofo", "hangul"):
        cp_group = rengi_06
      else:
        continue

      start = int(m.group("start"), 16)

      end = int(m.group("end"), 16) if m.group("end") is not None else start + 1

      for i in range(start, end):
        cp_group.add(i)

  with open(args.py_file, "w", encoding="utf-8") as f:

    f.write(
      TEMPLATE.format(
        codepoints_GCPY_12=",\n".join(map(str, gcpy_12)),
        codepoints_RENGI_06=",\n".join(map(str, rengi_06)),
        date=file_date,
        version=file_version
      )
    )
