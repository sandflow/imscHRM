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

'''Hypothetical Render Model (HRM)'''

__author__ = "Pierre-Anthony Lemieux <pal@palemieux.com>"

import typing
from dataclasses import dataclass
from fractions import Fraction
from numbers import Number
import logging

import ttconv.isd
import ttconv.style_properties as styles
import ttconv.model

from .codepoint_sets import GCPY_12, RENGI_06

LOGGER = logging.getLogger(__name__)

_BDRAW = 12
_GCPY_BASE = 12
_GCPY_OTHER = 3

_REN_G_CJK = 0.6
_REN_G_OTHER = 1.2

_NGBS = 1

_IPD = 1

@dataclass
class ISDStatistics:
  dur: Number = 0 # HRM ISD time
  dur_d: Number = 0 # HRM background drawing time
  nbg_total: Number = 0 # Number of backgrounds drawn
  clear: bool = False # Whether the root container had to be cleared
  dur_t: Number = 0 # HRM text drawing time
  ngra_t: Number = 0 # Total Normalized Rendered Glyph Area
  gcpy_count: Number = 0 # Total number of glyphs copied
  gren_count: Number = 0 # Total number of glyphs rendered
  is_empty: bool = False # Does the ISD contain any content


class EventHandler:
  '''Allows a callee to inform the caller of events that occur during processing. Typically
  overridden by the caller.
  '''
  
  @staticmethod
  def _format_message(msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: ISDStatistics):
    return (
      f"{msg} at {float(time_offset):.3f}s (doc #{doc_index})\n"
      f"  available time: {float(available_time):.3f}s | HRM time: {float(stats.dur):.3f}\n"
      f"  Glyph copy count: {stats.gcpy_count} | render count: {stats.gren_count} | Background draw count: {stats.nbg_total} | Clear: {stats.clear}\n"
    )


  def info(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: ISDStatistics):
    LOGGER.info(EventHandler._format_message(msg, doc_index, time_offset, available_time, stats))

  def warn(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: ISDStatistics):
    LOGGER.warning(EventHandler._format_message(msg, doc_index, time_offset, available_time, stats))

  def error(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: ISDStatistics):
    LOGGER.error(EventHandler._format_message(msg, doc_index, time_offset, available_time, stats))

  def debug(self, msg: str, doc_index: int, time_offset: Fraction, available_time: Fraction, stats: ISDStatistics):
    LOGGER.debug(EventHandler._format_message(msg, doc_index, time_offset, available_time, stats))


def validate(isd_iterator: typing.Iterator[typing.Tuple[Fraction, ttconv.isd.ISD]], event_handler: typing.Type[EventHandler]=EventHandler()):
  '''Determines whether the sequence of ISDs returned by `isd_iterator` conform to the IMSC HRM.
  `isd_iterator` returns a sequence of tuplets `(begin, ISD)`, where `ISD` is an ISD instance whose
  active interval starts at `begin` seconds and ends immediately before the `begin` value of the next 
  ISD. Errors, warnings and info messages are signalled through callbacks on the `event_handler`.
  '''

  hrm = HRM()

  last_render_time = -_IPD

  for doc_index, (time_offset, isd) in enumerate(isd_iterator):

    if time_offset <= last_render_time:
      raise RuntimeError("ISDs are not in order of increasing offset")

    stats = hrm.next_isd(isd)

    avail_render_time = min(_IPD, time_offset - last_render_time)

    event_handler.debug("Processed document", doc_index, time_offset, avail_render_time, stats)

    if not stats.is_empty:
      if stats.dur > avail_render_time:
        event_handler.error("Rendering time exceeded", doc_index, time_offset, avail_render_time, stats)

      if stats.ngra_t > _NGBS:
        event_handler.error("NGBS exceeded", doc_index, time_offset, avail_render_time, stats)

      last_render_time = time_offset


@dataclass(frozen=True)
class _Glyph:
  char: str
  color : styles.ColorType
  font_family: typing.Tuple[typing.Union[str, styles.GenericFontFamilyType]]
  font_size: styles.LengthType
  font_style: styles.FontStyleType
  font_weight: styles.FontWeightType
  text_decoration: styles.TextDecorationType
  text_outline: styles.TextOutlineType
  text_shadow: styles.TextShadowType
  background_color: styles.ColorType

class HRM:

  def __init__(self):
    self.back_buffer: typing.Set[_Glyph] = set()
    self.isd_stats: ISDStatistics = None
    
  def next_isd(
    self,
    isd: typing.Type[ttconv.isd.ISD]
    ) -> ISDStatistics:

    self.isd_stats = ISDStatistics()

    self._compute_dur_t(isd)

    self._compute_dur_d(isd)

    self.isd_stats.dur = self.isd_stats.dur_t + self.isd_stats.dur_d

    return self.isd_stats

  def _compute_dur_d(
    self,
    isd: typing.Type[ttconv.isd.ISD]
    ):

    self.isd_stats.is_empty = True

    draw_area = 0

    if isd is not None:
      for region in isd.iter_regions():

        if not _is_presented_region(region):
          continue

        self.isd_stats.is_empty = False

        nbg = 0

        for element in region.dfs_iterator():

          # should body elements really be excluded? -> NO
          # should transparent backgrounds really be counted? -> NO
          # should span and br really be included -> yes for now
          # should br really be included -> no

          if isinstance(element, ttconv.model.Br):
            continue

          bg_color = element.get_style(styles.StyleProperties.BackgroundColor)

          if bg_color is not None:
            if bg_color.ident is not styles.ColorType.Colorimetry.RGBA8:
              raise RuntimeError(f"Unsupported colorimetry system: {bg_color.ident}")

            if bg_color.components[3] != 0:
              nbg += 1

        draw_area += _region_normalized_size(region) * nbg

        self.isd_stats.nbg_total += nbg

    draw_area += 0 if self.isd_stats.is_empty else 1

    self.isd_stats.clear = draw_area != 0

    self.isd_stats.dur_d = draw_area / _BDRAW

  def _compute_dur_t(
    self,
    isd: typing.Type[ttconv.isd.ISD]
    ):

    front_buffer = set()

    if isd is not None:

      for region in isd.iter_regions():

        if not _is_presented_region(region):
          continue

        for element in region.dfs_iterator():

          if not isinstance(element, ttconv.model.Text):
            continue

          parent = element.parent()

          nrga = _compute_nrga(element)
          
          for char in element.get_text():

            glyph = _Glyph(
              char=char,
              color=parent.get_style(styles.StyleProperties.Color),
              font_family=parent.get_style(styles.StyleProperties.FontFamily),
              font_size=parent.get_style(styles.StyleProperties.FontSize),
              font_style=parent.get_style(styles.StyleProperties.FontStyle),
              font_weight=parent.get_style(styles.StyleProperties.FontWeight),
              text_decoration=parent.get_style(styles.StyleProperties.TextDecoration),
              text_outline=parent.get_style(styles.StyleProperties.TextOutline),
              text_shadow=parent.get_style(styles.StyleProperties.TextShadow),
              background_color=parent.get_style(styles.StyleProperties.BackgroundColor)
            )

            if glyph in front_buffer:

              self.isd_stats.dur_t += nrga / _compute_gcpy(char)

              self.isd_stats.gcpy_count += 1

            elif glyph in self.back_buffer:

              self.isd_stats.dur_t += nrga / _compute_gcpy(char)

              self.isd_stats.ngra_t += nrga

              self.isd_stats.gcpy_count += 1

            else:
              
              self.isd_stats.dur_t += nrga / _compute_ren_g(char)

              self.isd_stats.ngra_t += nrga

              self.isd_stats.gren_count += 1

            front_buffer.add(glyph)

    self.back_buffer = front_buffer

def _compute_nrga(element: typing.Type[ttconv.model.Text]):

  font_size: styles.LengthType = element.parent().get_style(styles.StyleProperties.FontSize)

  if font_size.units is not styles.LengthType.Units.rh:
    raise RuntimeError(f"Unsupported fontSize units: {font_size.units}")

  return font_size.value * font_size.value / 10000

def _compute_ren_g(char: str):

  if len(char) != 1:
    raise ValueError("Argument must be a string of length 1")

  return _REN_G_CJK if ord(char) in RENGI_06 else _REN_G_OTHER

def _compute_gcpy(char: str):

  if len(char) != 1:
    raise ValueError("Argument must be a string of length 1")

  return _GCPY_BASE if ord(char) in GCPY_12 else _GCPY_OTHER

def _region_normalized_size(region: typing.Type[ttconv.isd.ISD.Region]):

  region_extent: styles.ExtentType = region.get_style(styles.StyleProperties.Extent)

  if region_extent.width.units is not styles.LengthType.Units.rw:
    raise RuntimeError(f"Unsupported extent width units: {region_extent.width.units}")

  if region_extent.height.units is not styles.LengthType.Units.rh:
    raise RuntimeError(f"Unsupported extent height units: {region_extent.height.units}")

  return region_extent.width.value * region_extent.height.value / 10000

def _is_presented_region(region: typing.Type[ttconv.isd.ISD.Region]):
  '''See https://www.w3.org/TR/ttml-imsc1.1/#dfn-presented-region
  '''
  if region.get_style(styles.StyleProperties.Opacity) == 0:
    return False
  
  if region.get_style(styles.StyleProperties.Display) is styles.DisplayType.none:
    return False

  if region.get_style(styles.StyleProperties.Visibility) is styles.DisplayType.none:
    return False

  if region.has_children():
    return True

  if region.get_style(styles.StyleProperties.ShowBackground) is not styles.ShowBackgroundType.always:
    return False

  bg_color: styles.ColorType = region.get_style(styles.StyleProperties.BackgroundColor)

  if bg_color.ident is not styles.ColorType.Colorimetry.RGBA8:
    raise RuntimeError(f"Unsupported colorimetry system: {bg_color.ident}")

  if bg_color.components[3] == 0:
    return False

  return True
