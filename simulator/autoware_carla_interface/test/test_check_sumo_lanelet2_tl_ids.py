# Copyright 2024 Tier IV, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for tools/check_sumo_lanelet2_tl_ids.py; no CARLA, SUMO or ROS needed."""

import json
import os
import sys
import textwrap

sys.path.insert(
    0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
)

import check_sumo_lanelet2_tl_ids as tool  # noqa: E402

# tlLogic 1: landmark 10 on links 0-1, landmark 11 on link 2.
# tlLogic 2: landmark 12 on links 0-1, which differ (G/y) in the second phase.
_NET = textwrap.dedent("""\
    <net>
      <tlLogic id="1" type="static" programID="0" offset="0">
        <phase duration="42" state="Ggr"/>
        <phase duration="3" state="yyr"/>
        <phase duration="42" state="rrG"/>
        <param key="linkSignalID:0" value="10"/>
        <param key="linkSignalID:1" value="10"/>
        <param key="linkSignalID:2" value="11"/>
      </tlLogic>
      <tlLogic id="2" type="static" programID="0" offset="0">
        <phase duration="42" state="GG"/>
        <phase duration="3" state="Gy"/>
        <param key="linkSignalID:0" value="12"/>
        <param key="linkSignalID:1" value="12"/>
      </tlLogic>
    </net>
    """)


def _osm(ids):
    relations = "".join(
        f'<relation id="{i}"><tag k="type" v="regulatory_element"/>'
        f'<tag k="subtype" v="traffic_light"/></relation>'
        for i in ids
    )
    # A lanelet relation must not be counted.
    return f'<osm><relation id="99"><tag k="type" v="lanelet"/></relation>{relations}</osm>'


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text)
    return str(path)


def test_sumo_landmarks_and_mixed_states(tmp_path):
    landmarks, mixed = tool.sumo_landmarks(_write(tmp_path, "a.net.xml", _NET))
    assert landmarks == {"10": {"1"}, "11": {"1"}, "12": {"2"}}
    # G/g on landmark 10 is shown as green, so only landmark 12 is reported.
    assert mixed == [("2", "12", "Gy", "Gy")]


def test_matching_sides_pass(tmp_path, capsys):
    net = _write(tmp_path, "a.net.xml", _NET)
    osm = _write(tmp_path, "a.osm", _osm([10, 11, 12]))
    lights = [{"opendrive_id": i} for i in (10, 11, 12)]
    carla = _write(tmp_path, "c.json", json.dumps({"traffic_lights": lights}))
    assert tool.main([net, osm, "--carla-json", carla, "--report-mixed"]) == 0
    out = capsys.readouterr().out
    assert "INFO tlLogic 2: landmark 12" in out
    assert out.rstrip().endswith("OK")


def test_group_id_offset(tmp_path):
    net = _write(tmp_path, "a.net.xml", _NET)
    osm = _write(tmp_path, "a.osm", _osm([100010, 100011, 100012]))
    assert tool.main([net, osm, "--group-id-offset", "100000"]) == 0
    assert tool.main([net, osm]) == 1


def test_missing_and_split_landmarks_fail(tmp_path, capsys):
    net_text = _NET.replace('key="linkSignalID:1" value="12"', 'key="linkSignalID:1" value="10"')
    net = _write(tmp_path, "a.net.xml", net_text)
    osm = _write(tmp_path, "a.osm", _osm([10, 11, 13]))
    carla = _write(tmp_path, "c.json", json.dumps({"traffic_lights": [{"opendrive_id": 14}]}))
    assert tool.main([net, osm, "--carla-json", carla]) == 1
    out = capsys.readouterr().out
    assert "NG only in SUMO: ['12']" in out
    assert "NG only in Lanelet2 (or not an OpenDRIVE id): ['13']" in out
    assert "NG in CARLA but not in SUMO: ['14']" in out
    assert "NG in several tlLogics: ['10']" in out


def test_several_stop_positions_count_as_one_light(tmp_path, capsys):
    # As carla_tl_to_lanelet2.py writes a light with two lanes: the second regulatory element
    # gets a fresh id but refers to the same light heads as the first.
    def regelem(regelem_id, heads):
        members = "".join(f'<member type="way" ref="{h}" role="refers"/>' for h in heads)
        return (
            f'<relation id="{regelem_id}">{members}<tag k="subtype" v="traffic_light"/>'
            f'<tag k="type" v="regulatory_element"/></relation>'
        )

    relations = regelem(10, [1, 2]) + regelem(11, [3]) + regelem(12, [4]) + regelem(50, [2, 1])
    osm = _write(tmp_path, "a.osm", f"<osm>{relations}</osm>")
    assert tool.lanelet2_landmarks(osm) == ({"10", "11", "12"}, 4)
    assert tool.main([_write(tmp_path, "a.net.xml", _NET), osm]) == 0
    assert "Lanelet2: 3 traffic lights in 4 regulatory elements" in capsys.readouterr().out
