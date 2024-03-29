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

# pylint: disable=R0201,C0115,C0116,W0212
import unittest
from fractions import Fraction
import xml.etree.ElementTree as et

import ttconv.model as model
import ttconv.isd
import ttconv.style_properties as styles
import ttconv.imsc.reader
import imschrm.doc_sequence as doc_sequence
import imschrm.hrm as hrm

_BDRAW = 12
_GCPY_BASE = 12
_GCPY_OTHER = 3

_REN_G_CJK = 0.6
_REN_G_OTHER = 1.2

class InvalidError(RuntimeError):
  pass

class RaiseOnErrorHandler(hrm.EventHandler):
  def error(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: hrm.ISDStatistics):
    raise InvalidError()

class HRMValidator(unittest.TestCase):

  def test_doc_1(self):
    '''
    <region xml:id="r1" tts:extent="100% 100%"/>

    <body region="r1">
      <div>
        <p>
          <span>
            hello
          </span>
        </p>
      </div>
    </body>
    '''
    doc = model.ContentDocument()

    r1 = model.Region("r1", doc)
    r1.set_style(
      styles.StyleProperties.Extent,
      styles.ExtentType(
        height=styles.LengthType(value=100, units=styles.LengthType.Units.pct),
        width=styles.LengthType(value=100, units=styles.LengthType.Units.pct)
      )
    )
    doc.put_region(r1)

    b = model.Body(doc)
    b.set_region(r1)
    doc.set_body(b)

    div1 = model.Div(doc)
    b.push_child(div1)

    p1 = model.P(doc)
    div1.push_child(p1)

    span1 = model.Span(doc)
    p1.push_child(span1)

    t1 = model.Text(doc, "hello")
    span1.push_child(t1)
    
    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (4 / _REN_G_OTHER + 1 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 4)

    self.assertEqual(stats.gcpy_count, 1)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 4)

  def test_buffering_across_isds(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p begin="0s" end="1s">
        <span>hello</span>
      </p>
      <p begin="1s" end="2s">
        <span>bonjour bonjour</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    # isd at t = 0

    isd0 = ttconv.isd.ISD.from_model(doc, 0)

    stats = hrm_runner.next_isd(isd0) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (4 / _REN_G_OTHER + 1 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 4)

    self.assertEqual(stats.gcpy_count, 1)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 4)

    # isd at t = 1

    isd1 = ttconv.isd.ISD.from_model(doc, 1)

    stats = hrm_runner.next_isd(isd1) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (6 / _REN_G_OTHER + 9 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 6)

    self.assertEqual(stats.gcpy_count, 9)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 7)


  def test_buffering_across_isds_with_gap(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p begin="0s" end="0.5s">
        <span>hello</span>
      </p>
      <p begin="1s" end="2s">
        <span>bonjour bonjour</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    # isd at t = 0

    isd0 = ttconv.isd.ISD.from_model(doc, 0)

    stats = hrm_runner.next_isd(isd0) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (4 / _REN_G_OTHER + 1 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 4)

    self.assertEqual(stats.gcpy_count, 1)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 4)

    # isd at t = 0.5

    isd1 = ttconv.isd.ISD.from_model(doc, 0.5)

    stats = hrm_runner.next_isd(isd1)

    self.assertTrue(stats.is_empty)

    # isd at t = 1

    isd2 = ttconv.isd.ISD.from_model(doc, 1)

    stats = hrm_runner.next_isd(isd2) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (6 / _REN_G_OTHER + 9 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 6)

    self.assertEqual(stats.gcpy_count, 9)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 7)


  def test_doc_3(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>hello</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (4 / _REN_G_OTHER + 1 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 4)

    self.assertEqual(stats.gcpy_count, 1)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 4)

  def test_doc_4(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="50% 50%" tts:backgroundColor="black"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>abc</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0.25

    dur_t = 1/15 * 1/15 * (3 / _REN_G_OTHER)

    self.assertEqual(stats.gren_count, 3)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 1)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 3)

  def test_same_char_diff_color(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>hel</span><span tts:color="red">lo</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (5 / _REN_G_OTHER)

    self.assertEqual(stats.gren_count, 5)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 5)

  def test_cjk(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>你好</span><span>你好</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (2 / _REN_G_CJK + 2 / _GCPY_OTHER)

    self.assertEqual(stats.gren_count, 2)

    self.assertEqual(stats.gcpy_count, 2)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 2)

  def test_complex_non_cjk(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>Բարեւ</span><span>Բարեւ</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (5 / _REN_G_OTHER + 5 / _GCPY_OTHER)

    self.assertEqual(stats.gren_count, 5)

    self.assertEqual(stats.gcpy_count, 5)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 5)

  def test_multiple_regions(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="50% 50%" tts:backgroundColor="black"/>
      <region xml:id="r2" tts:origin="50% 50%" tts:extent="50% 50%" tts:backgroundColor="red"/>
      <region xml:id="r3" tts:origin="0% 50%" tts:extent="50% 50%" tts:backgroundColor="blue" />
    </layout>
  </head>
  <body>
    <div>
      <p region="r1">
        <span>abc</span>
      </p>
      <p region="r2">
        <span>abc</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd)

    clear_e_n = 1

    paint_e_n = 0.75

    dur_t = 1/15 * 1/15 * (3 / _REN_G_OTHER + 3 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 3)

    self.assertEqual(stats.gcpy_count, 3)

    self.assertEqual(stats.nbg_total, 3)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 3)

  def test_multiple_bg_color(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="50% 50%" tts:backgroundColor="red"/>
    </layout>
  </head>
  <body tts:backgroundColor="blue" region="r1" >
    <div tts:backgroundColor="black">
      <p tts:backgroundColor="white">
        <span tts:backgroundColor="green">hel</span><span tts:backgroundColor="gray">lo</span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0.25 * 6

    dur_t = 1/15 * 1/15 * (5 / _REN_G_OTHER + 0 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 5)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 6)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 5)

  def test_null_isd(self):

    hrm_runner = hrm.HRM()

    stats = hrm_runner.next_isd(None) 

    self.assertAlmostEqual(stats.dur, 0)

    self.assertAlmostEqual(stats.ngra_t, 0)
    
    self.assertEqual(stats.gren_count, 0)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 0)

    stats = hrm_runner.next_isd(None) 

    self.assertAlmostEqual(stats.dur, 0)

    self.assertAlmostEqual(stats.ngra_t, 0)

    self.assertEqual(stats.gren_count, 0)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 0)

  def test_br_ignored(self):
    """Confirm that BR elements are excluded from NBG(Ri) computations
    """

    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:extent="100% 100%"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p>
        <span>hello<br tts:backgroundColor="blue"/></span>
      </p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    # create ISDs

    isd = ttconv.isd.ISD.from_model(doc, 0)

    # run HRM

    stats = hrm_runner.next_isd(isd) 

    clear_e_n = 1

    paint_e_n = 0

    dur_t = 1/15 * 1/15 * (4 / _REN_G_OTHER + 1 / _GCPY_BASE)

    self.assertEqual(stats.gren_count, 4)

    self.assertEqual(stats.gcpy_count, 1)

    self.assertEqual(stats.nbg_total, 0)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 1/15 * 1/15 * 4)

  def test_exceed_ipd(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:backgroundColor="black"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p begin="0s" end="1s">0</p>
      <p begin="2s" end="3s" tts:fontSize="300%">abcdefghijklmnopqrstuvwxy</p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    isd_list = ttconv.isd.ISD.generate_isd_sequence(doc)

    hrm_runner.next_isd(isd_list[0][1])
    hrm_runner.next_isd(isd_list[1][1])
    stats = hrm_runner.next_isd(isd_list[2][1])

    clear_e_n = 1

    paint_e_n = 1

    dur_t = 3/15 * 3/15 * (25 / _REN_G_OTHER)

    self.assertEqual(stats.gren_count, 25)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 1)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 3/15 * 3/15 * 25)

    # expect failed validation

    eh = RaiseOnErrorHandler()

    with self.assertRaises(InvalidError):
      hrm.validate(iter(isd_list), eh)

  def test_ipd(self):
    ttml_doc = '''<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:backgroundColor="black"/>
    </layout>
  </head>
  <body region="r1">
    <div>
      <p begin="0s" end="1s" tts:fontSize="300%">abcdefghijklmnopqrstuvwx</p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    hrm_runner = hrm.HRM()

    isd_list = ttconv.isd.ISD.generate_isd_sequence(doc)

    stats = hrm_runner.next_isd(isd_list[0][1])

    clear_e_n = 1

    paint_e_n = 1

    dur_t = 3/15 * 3/15 * (24 / _REN_G_OTHER)

    self.assertEqual(stats.gren_count, 24)

    self.assertEqual(stats.gcpy_count, 0)

    self.assertEqual(stats.nbg_total, 1)

    self.assertAlmostEqual(stats.dur, (clear_e_n + paint_e_n) / _BDRAW + dur_t)

    self.assertAlmostEqual(stats.ngra_t, 3/15 * 3/15 * 24)

    # expect failed validation

    eh = RaiseOnErrorHandler()

    hrm.validate(iter(isd_list), eh)

  def test_show_background(self):
    ttml_doc = '''<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:timeBase="media">
  <head>
    <styling>
      <style xml:id="s1" tts:backgroundColor="#ff0000" />
    </styling>
    <layout>
      <region xml:id="r1" style="s1" tts:extent="50% 50%" tts:origin="0% 0%"/>
      <region xml:id="r4" tts:extent="50% 50%" tts:origin="50% 0%"/>
    </layout>
  </head>
  <body>
    <div>
      <p region="r4" begin="00:00:00" end="00:00:00.2" xml:id="p0">ABCDEF</p>
      <p region="r1" begin="00:00:00.25" end="00:00:04" xml:id="p1"><span style="s1">a</span></p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # expect failed validation since there a cost to drawing r1 between the two <p>
    eh = RaiseOnErrorHandler()
    with self.assertRaises(InvalidError):
      hrm.validate(doc_sequence.iter_isd([(0, None, ttml_doc)]), eh)

  def test_unassociated_p(self):
    ttml_doc = '''<tt xml:lang="en"
    xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <layout>
      <region xml:id="r1" tts:backgroundColor="#ff0000"></region>
    </layout>
  </head>
  <body>
    <div>
      <p xml:id="p0" begin="00:00:02.9" end="00:00:03"></p>
      <p xml:id="p1" region="r1" begin="00:00:03" end="00:00:04">hello</p>
    </div>
  </body>
</tt>'''

    doc = ttconv.imsc.reader.to_model(et.ElementTree(et.fromstring(ttml_doc)))

    # expect failed validation since p0 generates an ISD even though it contains not textual content because the region has a background
    eh = RaiseOnErrorHandler()
    with self.assertRaises(InvalidError):
      hrm.validate(doc_sequence.iter_isd([(0, None, ttml_doc)]), eh)

if __name__ == '__main__':
  unittest.main()
