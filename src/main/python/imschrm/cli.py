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

'''Hypothetical Render Model (HRM) Validator'''

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

import argparse
import sys
import logging
from fractions import Fraction
import os.path
import json

import imschrm.hrm
import imschrm.doc_sequence

logging.basicConfig(level=logging.WARNING)

LOGGER = logging.getLogger("hrm-validator")

class EventHandler(imschrm.hrm.EventHandler):

  def __init__(self):
    self.failed = False

  def error(self, msg: str, doc_index: int, time_offset: Fraction):
    self.failed = True
    super().error(msg, doc_index, time_offset)


class LocalFileSequence:

  def __init__(self, manifest_path):
    with open(manifest_path) as f: 
      self.manifest = json.load(f)

    self.root_path = os.path.dirname(manifest_path)

  def __iter__(self):
    for document in self.manifest:
      with open(os.path.join(self.root_path, document["path"])) as f:
        yield (Fraction(document["begin"]), None if document["end"] is None else Fraction(document["end"]), f.read())


class SingleLocalFile:
  def __init__(self, path):
    self.path = path

  def __iter__(self):
    with open(self.path, "r", encoding="utf-8") as f:
      yield (0, None, f.read())
      

def main(argv=None):
  '''Main application processing'''

  parser = argparse.ArgumentParser(description='Verifies that an IMSC document conforms to the HRM')
  parser.add_argument('input', help='Path to the input document')
  parser.add_argument('--itype', choices=['ttml', 'manifest'], default="ttml", help='Type of input')

  args = parser.parse_args(argv)

  ev = EventHandler()

  if args.itype is None or args.itype == "ttml":
    doc_sequence = SingleLocalFile(args.input)
  else:
    doc_sequence = LocalFileSequence(args.input)

  imschrm.hrm.validate(imschrm.doc_sequence.iter_isd(doc_sequence), ev)

  if ev.failed:
    print("Validation failed")
    sys.exit(1)

if __name__ == "__main__":
  main()
