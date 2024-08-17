#!/usr/bin/env python3
# Copyright (C) 2024 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from python.generators.diff_tests.testing import Csv, Path, DataPath
from python.generators.diff_tests.testing import DiffTestBlueprint
from python.generators.diff_tests.testing import TestSuite


class WattsonStdlib(TestSuite):
  consolidate_tables_template = ('''
      SELECT
        sum(dur) as duration,
        SUM(l3_hit_count) AS l3_hit_count,
        SUM(l3_miss_count) AS l3_miss_count,
        freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
        freq_4, idle_4, freq_5, idle_5, freq_6, idle_6, freq_7, idle_7,
        suspended
      FROM SYSTEM_STATE_TABLE
      GROUP BY
        freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
        freq_4, idle_4, freq_5, idle_5, freq_6, idle_6, freq_7, idle_7,
        suspended
      ORDER BY duration desc
      LIMIT 20;
      ''')

  # Test raw system state before any grouping
  def test_wattson_system_state(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;
        SELECT * from wattson_system_states
        ORDER by ts DESC
        LIMIT 20
        """,
        out=Csv("""
        "ts","dur","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
        370103436540,339437,"[NULL]","[NULL]",738000,-1,738000,1,738000,-1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103419857,16683,"[NULL]","[NULL]",738000,-1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103213314,206543,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,1,1106000,1,0
        370103079729,133585,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,-1,400000,1,1106000,-1,1106000,1,0
        370102869076,210653,"[NULL]","[NULL]",738000,1,738000,1,738000,1,738000,-1,400000,1,400000,1,1106000,-1,1106000,1,0
        370102837378,31698,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,1106000,-1,1106000,1,0
        370102832862,4516,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,1106000,-1,1106000,-1,0
        370102831844,1018,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,1106000,-1,984000,-1,0
        370102819475,12369,"[NULL]","[NULL]",738000,1,738000,1,738000,-1,738000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102816586,1098,"[NULL]","[NULL]",738000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102669043,147543,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,-1,984000,-1,0
        370102044564,624479,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,1,400000,1,400000,1,984000,-1,984000,-1,0
        370100810360,1234204,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,1,400000,1,400000,1,984000,1,984000,-1,0
        370100731096,79264,"[NULL]","[NULL]",574000,1,574000,1,574000,-1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100411312,319784,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100224219,187093,"[NULL]","[NULL]",574000,-1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370100171729,52490,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,-1,400000,1,400000,1,984000,1,984000,-1,0
        370096452775,3718954,"[NULL]","[NULL]",574000,1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,1,984000,-1,0
        370096412858,39917,"[NULL]","[NULL]",574000,-1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,1,984000,-1,0
        370096347307,65551,"[NULL]","[NULL]",574000,-1,574000,1,574000,1,574000,1,400000,1,400000,1,984000,-1,984000,-1,0
            """))

  # Test fixup of deep idle offset and time marker window.
  def test_wattson_time_window(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;

        CREATE PERFETTO TABLE wattson_time_window
        AS
        SELECT 362426061658 AS ts, 5067704349 AS dur;

        -- Final table that is cut off to fit within the requested time window.
        CREATE VIRTUAL TABLE time_window_intersect
          USING SPAN_JOIN(wattson_system_states, wattson_time_window);
        """ + self.consolidate_tables_template.replace("SYSTEM_STATE_TABLE",
                                                       "time_window_intersect"),
        out=Csv("""
            "duration","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
            59232508,2796301,1232977,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,1,500000,0,0
            50664181,2364802,1133322,574000,0,574000,1,574000,1,574000,0,553000,1,553000,0,500000,0,500000,0,0
            41917186,2020898,920691,574000,0,574000,0,574000,1,574000,1,553000,0,553000,0,500000,0,500000,1,0
            33778317,1478303,683731,300000,0,300000,0,300000,1,300000,1,400000,0,400000,0,500000,0,500000,1,0
            32703489,1428203,690001,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            28770906,1588177,715673,574000,0,574000,0,574000,1,574000,0,553000,1,553000,0,500000,1,500000,0,0
            28310872,1211262,566873,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            26754474,1224826,569901,300000,0,300000,1,300000,0,300000,0,400000,1,400000,0,500000,0,500000,0,0
            24816645,1047517,467614,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,1,500000,0,0
            24251986,984546,417947,300000,0,300000,0,300000,1,300000,0,400000,1,400000,0,500000,1,500000,0,0
            23771603,987803,450930,300000,0,300000,1,300000,1,300000,0,400000,1,400000,0,500000,0,500000,0,0
            22988523,984240,473025,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,1,0
            22057168,998933,453689,300000,0,300000,1,300000,1,300000,0,400000,0,400000,0,500000,0,500000,1,0
            21663200,1034424,445500,574000,0,574000,0,574000,1,574000,0,553000,0,553000,0,500000,0,500000,1,0
            20665650,974100,442861,300000,0,300000,0,300000,1,300000,0,400000,0,400000,1,500000,0,500000,0,0
            18224891,834959,345078,300000,0,300000,1,300000,0,300000,0,400000,0,400000,0,500000,1,500000,0,0
            17469272,816735,342795,574000,0,574000,0,574000,0,574000,0,553000,1,553000,0,500000,1,500000,0,0
            16560058,754170,344777,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,0,500000,1,0
            16191449,689792,316923,300000,0,300000,0,300000,1,300000,0,400000,1,400000,0,500000,0,500000,0,0
            16008137,748321,327736,574000,0,574000,1,574000,0,574000,1,553000,0,553000,0,500000,1,500000,0,0
            """))

  # Test on Raven for checking system states and the DSU PMU counts.
  def test_wattson_dsu_pmu(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("INCLUDE PERFETTO MODULE wattson.system_state;\n" +
               self.consolidate_tables_template.replace(
                   "SYSTEM_STATE_TABLE", "wattson_system_states")),
        out=Csv("""
            "duration","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","suspended"
            1280071578,1319309,419083,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            165833778,118250,42072,300000,-1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            121848767,5879527,2358273,574000,0,574000,1,574000,0,574000,0,553000,0,553000,0,500000,1,500000,1,0
            72914132,134731,58480,300000,1,300000,1,300000,-1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            70723657,68341,22021,300000,1,300000,-1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            64738046,275953,309822,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,-1,500000,1,0
            59232508,2796301,1232977,574000,0,574000,1,574000,1,574000,0,553000,0,553000,0,500000,1,500000,0,0
            50960835,50577,17976,300000,1,300000,1,300000,1,300000,-1,400000,1,400000,1,500000,1,500000,1,0
            50664181,2364802,1133322,574000,0,574000,1,574000,1,574000,0,553000,1,553000,0,500000,0,500000,0,0
            49614333,2201254,928640,300000,0,300000,1,300000,0,300000,0,400000,0,400000,0,500000,1,500000,1,0
            41917186,2020898,920691,574000,0,574000,0,574000,1,574000,1,553000,0,553000,0,500000,0,500000,1,0
            40469221,"[NULL]","[NULL]",1401000,1,1401000,1,1401000,1,1401000,1,400000,1,400000,1,2802000,1,2802000,1,0
            40265209,14021,1245,300000,0,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,1,0
            38159789,1428203,690001,300000,0,300000,0,300000,1,300000,0,400000,0,400000,0,500000,0,500000,0,0
            33778317,1478303,683731,300000,0,300000,0,300000,1,300000,1,400000,0,400000,0,500000,0,500000,1,0
            31421773,34528,17983,300000,1,300000,1,300000,1,300000,1,400000,-1,400000,1,500000,1,500000,1,0
            31137678,162530,198792,1098000,1,1098000,1,1098000,1,1098000,1,400000,1,400000,1,500000,1,500000,-1,0
            30271091,38946,48402,300000,1,300000,1,300000,1,300000,1,400000,1,400000,1,500000,1,500000,-1,0
            30209881,"[NULL]","[NULL]",1328000,1,1328000,1,1328000,1,1328000,1,2253000,1,2253000,1,500000,1,500000,1,0
            30118849,1394832,585081,574000,0,574000,1,574000,0,574000,0,553000,0,553000,0,500000,1,500000,0,0
            """))

  # Test on eos to check that suspend states are being calculated appropriately.
  def test_wattson_suspend(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query="""
        INCLUDE PERFETTO MODULE wattson.system_state;
        SELECT
          sum(dur) as duration,
          freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
          suspended
        FROM wattson_system_states
        GROUP BY
          freq_0, idle_0, freq_1, idle_1, freq_2, idle_2, freq_3, idle_3,
          suspended
        ORDER BY duration desc
        LIMIT 20;
        """,
        out=Csv("""
            "duration","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","suspended"
            16606175990,614400,1,614400,1,614400,1,614400,1,0
            10648392546,1708800,-1,1708800,-1,1708800,-1,1708800,-1,1
            6972220533,1708800,-1,1708800,-1,1708800,-1,1708800,-1,0
            1649400745,614400,0,614400,0,614400,0,614400,0,0
            1206977074,614400,-1,614400,1,614400,1,614400,1,0
            945900007,1708800,0,1708800,0,1708800,0,1708800,0,0
            943703078,1363200,0,1363200,0,1363200,0,1363200,1,0
            736663600,1708800,0,1708800,0,1708800,0,1708800,1,0
            706695995,1708800,1,1708800,1,1708800,1,1708800,1,0
            656873956,1363200,1,1363200,1,1363200,1,1363200,1,0
            633440914,1363200,0,1363200,0,1363200,0,1363200,0,0
            627957352,1708800,-1,1708800,0,1708800,0,1708800,0,0
            615611076,1708800,-1,1708800,1,1708800,1,1708800,1,0
            575584212,1708800,-1,1708800,0,1708800,0,1708800,-1,0
            527581753,1708800,-1,1708800,-1,1708800,0,1708800,-1,0
            488107828,1708800,0,1708800,0,1708800,0,1708800,-1,0
            474912603,1363200,-1,1363200,0,1363200,0,1363200,1,0
            461943392,1708800,0,1708800,-1,1708800,0,1708800,0,0
            375051979,864000,1,864000,1,864000,1,864000,1,0
            371458882,1363200,-1,1363200,0,1363200,0,1363200,-1,0
            """))

  # Test that the device name can be extracted from the trace's metadata.
  def test_wattson_device_name(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_wo_device_name.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.device_infos;
            select name from _wattson_device
            """),
        out=Csv("""
            "name"
            "monaco"
            """))

  # Tests intermediate table
  def test_wattson_intermediate_table(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.ungrouped;
              select * from _w_independent_cpus_calc
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 10
            """),
        out=Csv("""
            "ts","dur","l3_hit_count","l3_miss_count","freq_0","idle_0","freq_1","idle_1","freq_2","idle_2","freq_3","idle_3","freq_4","idle_4","freq_5","idle_5","freq_6","idle_6","freq_7","idle_7","policy_4","policy_5","policy_6","policy_7","no_static","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_4","static_5","static_6","static_7"
            359661672578,75521,8326,9689,1401000,0,1401000,0,1401000,0,1401000,0,2253000,-1,2253000,0,2802000,-1,2802000,0,4,4,6,6,0,"[NULL]","[NULL]","[NULL]","[NULL]",527.050000,23.500000,1942.890000,121.430000,35.660000,-1.000000,35.640000,-1.000000
            359661748099,2254517,248577,289258,1401000,0,1401000,0,1401000,0,1401000,0,2253000,0,2253000,0,2802000,-1,2802000,0,4,4,6,6,0,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,23.500000,1942.890000,121.430000,-1.000000,-1.000000,35.640000,-1.000000
            359664003674,11596,1278,1487,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,-1,2253000,-1,2802000,-1,2802000,-1,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",527.050000,527.050000,1942.890000,1942.890000,35.660000,35.660000,35.640000,35.640000
            359664015270,4720,520,605,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,-1,2253000,-1,2802000,-1,2802000,0,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",527.050000,527.050000,1942.890000,121.430000,35.660000,35.660000,35.640000,-1.000000
            359664019990,18921,2086,2427,1401000,-1,1401000,-1,1401000,-1,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,527.050000,1942.890000,121.430000,-1.000000,35.660000,35.640000,-1.000000
            359664038911,8871,978,1138,1401000,-1,1401000,-1,1401000,0,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,527.050000,1942.890000,121.430000,-1.000000,35.660000,35.640000,-1.000000
            359664047782,1343,148,172,1401000,-1,1401000,0,1401000,0,1401000,-1,2253000,0,2253000,-1,2802000,-1,2802000,0,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,527.050000,1942.890000,121.430000,-1.000000,35.660000,35.640000,-1.000000
            359664049491,1383,152,177,1401000,0,1401000,0,1401000,0,1401000,-1,2253000,0,2253000,0,2802000,-1,2802000,0,4,4,6,6,-1,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,23.500000,1942.890000,121.430000,-1.000000,-1.000000,35.640000,-1.000000
            359664050874,2409912,265711,309195,1401000,0,1401000,0,1401000,0,1401000,0,2253000,0,2253000,0,2802000,-1,2802000,0,4,4,6,6,0,"[NULL]","[NULL]","[NULL]","[NULL]",23.500000,23.500000,1942.890000,121.430000,-1.000000,-1.000000,35.640000,-1.000000
            359666460786,13754,1516,1764,1401000,0,1401000,0,1401000,0,1401000,0,2253000,-1,2253000,0,2802000,-1,2802000,0,4,4,6,6,0,"[NULL]","[NULL]","[NULL]","[NULL]",527.050000,23.500000,1942.890000,121.430000,35.660000,-1.000000,35.640000,-1.000000
            """))

  # Tests that device static curve selection is only when CPUs are active
  def test_wattson_static_curve_selection(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.ungrouped;
              select * from _system_state_curves
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            359085636893,23030,0.000000,"[NULL]",0.000000,0.000000,0.000000,28.510000,0.000000,0.000000,0.000000,"[NULL]","[NULL]"
            359085659923,6664673,0.000000,"[NULL]",0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            359092324596,1399699,0.000000,"[NULL]",0.000000,21.840000,0.000000,0.000000,0.000000,0.000000,3.730000,"[NULL]","[NULL]"
            359093724295,6959391,0.000000,"[NULL]",0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000
            359100683686,375122,0.000000,"[NULL]",0.000000,0.000000,28.510000,0.000000,0.000000,0.000000,0.000000,"[NULL]","[NULL]"
            """))

  # Tests that L3 cache calculations are being done correctly
  def test_wattson_l3_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.ungrouped;
              select * from _system_state_curves
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            359661672578,75521,3.410000,3.410000,3.410000,3.410000,527.050000,23.500000,1942.890000,121.430000,35.660000,16836.004600,1215.000600
            359661748099,2254517,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,35.640000,578637.540600,262212.377000
            359664003674,11596,248.900000,248.900000,248.900000,248.900000,527.050000,527.050000,1942.890000,1942.890000,35.660000,2584.243800,186.469800
            359664015270,4720,248.900000,248.900000,248.900000,248.900000,527.050000,527.050000,1942.890000,121.430000,35.660000,1051.492000,75.867000
            359664019990,18921,248.900000,248.900000,248.900000,248.900000,23.500000,527.050000,1942.890000,121.430000,35.660000,4218.100600,304.345800
            """))

  # Tests calculations when everything in system state is converted to mW
  def test_wattson_system_state_mw_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.ungrouped;
              select * from _system_state_mw
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 10
            """),
        out=Csv("""
            "ts","dur","cpu0_mw","cpu1_mw","cpu2_mw","cpu3_mw","cpu4_mw","cpu5_mw","cpu6_mw","cpu7_mw","dsu_scu_mw"
            359661672578,75521,3.410000,3.410000,3.410000,3.410000,527.050000,23.500000,1942.890000,121.430000,274.679679
            359661748099,2254517,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,408.602332
            359664003674,11596,248.900000,248.900000,248.900000,248.900000,527.050000,527.050000,1942.890000,1942.890000,274.597013
            359664015270,4720,248.900000,248.900000,248.900000,248.900000,527.050000,527.050000,1942.890000,121.430000,274.507246
            359664019990,18921,248.900000,248.900000,248.900000,248.900000,23.500000,527.050000,1942.890000,121.430000,274.677304
            359664038911,8871,248.900000,248.900000,3.410000,248.900000,23.500000,527.050000,1942.890000,121.430000,274.676909
            359664047782,1343,248.900000,3.410000,3.410000,248.900000,23.500000,527.050000,1942.890000,121.430000,274.557692
            359664049491,1383,3.450000,3.450000,3.450000,208.140000,23.500000,23.500000,1942.890000,121.430000,407.495459
            359664050874,2409912,3.450000,3.450000,3.450000,3.450000,23.500000,23.500000,1942.890000,121.430000,408.602720
            359666460786,13754,3.410000,3.410000,3.410000,3.410000,527.050000,23.500000,1942.890000,121.430000,274.623880
            """))

  # Tests that suspend values are being skipped
  def test_wattson_suspend_calculations(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.ungrouped;
              select * from _system_state_curves
              WHERE ts > 24790009884888
              ORDER by ts ASC
              LIMIT 5
            """),
        out=Csv("""
            "ts","dur","cpu0_curve","cpu1_curve","cpu2_curve","cpu3_curve","cpu4_curve","cpu5_curve","cpu6_curve","cpu7_curve","static_curve","l3_hit_value","l3_miss_value"
            24790009907857,2784616769,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0.000000,0,0
            24792794524626,424063,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792794948689,205625,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792795154314,19531,39.690000,39.690000,39.690000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            24792795173845,50781,39.690000,39.690000,0.000000,39.690000,0.000000,0.000000,0.000000,0.000000,18.390000,"[NULL]","[NULL]"
            """))

  # Tests that device curve table is being looked up correctly
  def test_wattson_device_curve_per_policy(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.grouped;
              select * from wattson_estimate_per_component
              WHERE ts > 359661672577
              ORDER by ts ASC
              LIMIT 10
            """),
        out=Csv("""
            "ts","dur","l3","little_cpus","mid_cpus","big_cpus"
            359661672578,75521,18051.005200,49.300000,550.550000,2064.320000
            359661748099,2254517,840849.917600,49.440000,47.000000,2064.320000
            359664003674,11596,2770.713600,1031.260000,1054.100000,3885.780000
            359664015270,4720,1127.359000,1031.260000,1054.100000,2064.320000
            359664019990,18921,4522.446400,1031.260000,550.550000,2064.320000
            359664038911,8871,2120.319000,785.770000,550.550000,2064.320000
            359664047782,1343,320.839600,540.280000,550.550000,2064.320000
            359664049491,1383,514.276100,254.130000,47.000000,2064.320000
            359664050874,2409912,898807.333300,49.440000,47.000000,2064.320000
            359666460786,13754,3286.709200,49.300000,550.550000,2064.320000
            """))

  # Tests that total calculations are correct
  def test_wattson_total_raven_calc(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_dsu_pmu.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.grouped;
               select * from _wattson_entire_trace
            """),
        out=Csv("""
            "total_l3","total_little_cpus","total_mid_cpus","total_big_cpus","total"
            500.010000,662.000000,370.730000,1490.770000,3023.520000
            """))

  # Tests that total calculations are correct
  def test_wattson_total_eos_calc(self):
    return DiffTestBlueprint(
        trace=DataPath('wattson_eos_suspend.pb'),
        query=("""
            INCLUDE PERFETTO MODULE wattson.curves.grouped;
               select * from _wattson_entire_trace
            """),
        out=Csv("""
            "total_l3","total_little_cpus","total_mid_cpus","total_big_cpus","total"
            0.000000,2602.930000,0.000000,0.000000,2602.930000
            """))
