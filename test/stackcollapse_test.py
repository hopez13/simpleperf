#!/usr/bin/env python3
#
# Copyright (C) 2021 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from pathlib import Path

from . test_utils import TestBase, TestHelper


class TestStackCollapse(TestBase):

    def test_jit_annotations(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_jit_symbol.data'),
            '--jit',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_jit_symbol.foldedstack')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_kernel_annotations(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_trace_offcpu.data'),
            '--kernel',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_trace_offcpu.foldedstack')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_with_pid(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_jit_symbol.data'),
            '--jit',
            '--pid',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_jit_symbol.foldedstack_with_pid')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_with_tid(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_jit_symbol.data'),
            '--jit',
            '--tid',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_jit_symbol.foldedstack_with_tid')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_two_event_types_chooses_first(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_two_event_types.data'),
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_two_event_types.foldedstack')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_two_event_types_chooses_with_event_filter(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_two_event_types.data'),
            '--event-filter', 'cpu-clock',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_two_event_types.foldedstack_cpu_clock')
        self.assertEqual(got, Path(golden_path).read_text())

    def test_unknown_symbol_addrs(self):
        got = self.run_cmd([
            'stackcollapse.py',
            '-i', TestHelper.testdata_path('perf_with_jit_symbol.data'),
            '--addrs',
        ], return_output=True)
        golden_path = TestHelper.testdata_path('perf_with_jit_symbol.foldedstack_addrs')
        self.assertEqual(got, Path(golden_path).read_text())
