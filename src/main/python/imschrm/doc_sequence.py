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

"""Processes a sequence of IMSC documents into a sequence of ISDs"""

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

import xml.etree.ElementTree as et
import itertools
import typing
from numbers import Number

import ttconv.imsc.reader
import ttconv.isd

def _pairwise(iterable):
  a, b = itertools.tee(iterable)
  next(b, None)
  return zip(a, b)

DocumentIterator = typing.Iterator[typing.Tuple[Number, Number, str]]

def iter_isd(doc_iterator: DocumentIterator, tolerance=0):
  '''Iterates through the ISDs resulting from a sequence of TTML documents obtained from `doc_iterator`.
  `doc_iterator` returns a sequence of tuplets `(begin, end, doc)`, where `doc` is a string representation of
  a valid TTML document active in the interval `[begin, end)` expressed in seconds. The intervals are
  non-overlapping and sorted in order of increasing `begin` time. `tolerance` specifies the numerical
  tolerance to use when comparing document intervals.
  '''
  
  cur_time = None

  for doc_begin, doc_end, ttml_doc in doc_iterator:

    if cur_time is not None:

      if cur_time - doc_begin > tolerance:

        raise RuntimeError("Time intervals are overlapping.")

      if doc_begin - cur_time > tolerance:

        # insert a null ISD if there is a gap between documents

        yield (cur_time, None)
      
    cur_time = doc_begin

    m = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    sig_times = ttconv.isd.ISD.significant_times(m)

    for left_side, right_side in _pairwise(tuple(sig_times) + (None,)):

      if cur_time - left_side >= (-tolerance) and (right_side is None or right_side - cur_time > (-tolerance) ):

        yield (cur_time, ttconv.isd.ISD.from_model(m, left_side, sig_times))

        if right_side is None:
          return

        cur_time = right_side

      if doc_end is not None and cur_time - doc_end >= (-tolerance):
        cur_time = doc_end
        break
