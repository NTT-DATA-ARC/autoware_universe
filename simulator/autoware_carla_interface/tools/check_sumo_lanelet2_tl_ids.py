#!/usr/bin/env python3
"""
Check that a SUMO net and a Lanelet2 map refer to the same CARLA traffic lights.

A CARLA traffic light is identified by its OpenDRIVE landmark id, which appears in
- the SUMO net: <param key="linkSignalID:<linkIndex>" value="<landmark>"/> of each tlLogic
  (added by ~/CARLA/Co-Simulation/Sumo/util/add_carla_tls.py), and
- the Lanelet2 map: the id of each traffic_light regulatory element, minus --group-id-offset
  (added by tools/carla_tl_to_lanelet2.py).
This tool reports the landmarks found on only one side, landmarks split over several tlLogics,
and, with --carla-json (the --dump-json output of carla_tl_to_lanelet2.py), CARLA lights
missing from either side.

With --report-mixed it also lists the landmarks whose SUMO links show different states in
one phase. The co-simulation bridge forces such a CARLA light to red for that phase
(sumo_integration/bridge_helper.py get_carla_traffic_light_state); only the G/g mix is
shown as green and is not reported.

Usage:
    python3 tools/check_sumo_lanelet2_tl_ids.py NET.net.xml MAP_with_tl.osm \
        [--carla-json carla_tl.json] [--group-id-offset N] [--report-mixed]
Exit status: 0 if both sides agree, 1 otherwise.
"""

import argparse
import json
import sys
import xml.etree.ElementTree as ET


def sumo_landmarks(net_path):
    """Return ({landmark: {tlLogic id}}, [(tlLogic id, landmark, phase state, states)])."""
    root = ET.parse(net_path).getroot()
    landmarks = {}
    mixed = []
    for tl in root.findall("tlLogic"):
        links = {}
        for param in tl.findall("param"):
            key = param.get("key", "")
            if key.startswith("linkSignalID:"):
                links[int(key.split(":")[1])] = param.get("value")
                landmarks.setdefault(param.get("value"), set()).add(tl.get("id"))
        phases = [phase.get("state") for phase in tl.findall("phase")]
        for landmark in sorted(set(links.values())):
            indices = [i for i, value in links.items() if value == landmark]
            for state in phases:
                states = {state[i] for i in indices if i < len(state)}
                if len(states) > 1 and not states <= {"G", "g"}:
                    mixed.append((tl.get("id"), landmark, state, "".join(sorted(states))))
                    break
    return landmarks, mixed


def lanelet2_landmarks(osm_path, group_id_offset=0):
    """Return the landmark ids of the traffic_light regulatory elements of a Lanelet2 map."""
    root = ET.parse(osm_path).getroot()
    ids = set()
    for relation in root.findall("relation"):
        tags = {tag.get("k"): tag.get("v") for tag in relation.findall("tag")}
        if tags.get("type") == "regulatory_element" and tags.get("subtype") == "traffic_light":
            ids.add(str(int(relation.get("id")) - group_id_offset))
    return ids


def carla_landmarks(json_path):
    """Return the OpenDRIVE ids of a carla_tl_to_lanelet2.py --dump-json file."""
    with open(json_path) as f:
        return {str(light["opendrive_id"]) for light in json.load(f)["traffic_lights"]}


def _sorted_ids(ids):
    return sorted(ids, key=lambda s: (len(s), s))


def check(net_path, osm_path, carla_json=None, group_id_offset=0, report_mixed=False):
    """Print the comparison and return True if both sides agree."""
    sumo, mixed = sumo_landmarks(net_path)
    lanelet2 = lanelet2_landmarks(osm_path, group_id_offset)
    sumo_ids = set(sumo)
    problems = []

    print(f"SUMO: {len(sumo_ids)} landmarks in {len(set().union(*sumo.values()))} tlLogics")
    print(
        f"Lanelet2: {len(lanelet2)} traffic-light regulatory elements "
        f"(group id offset {group_id_offset})"
    )
    problems.append(("only in SUMO", sumo_ids - lanelet2))
    problems.append(("only in Lanelet2 (or not an OpenDRIVE id)", lanelet2 - sumo_ids))
    if carla_json:
        carla = carla_landmarks(carla_json)
        print(f"CARLA: {len(carla)} traffic lights")
        problems.append(("in CARLA but not in SUMO", carla - sumo_ids))
        problems.append(("in CARLA but not in Lanelet2", carla - lanelet2))
    problems.append(
        ("in several tlLogics", {landmark for landmark, tls in sumo.items() if len(tls) > 1})
    )

    ok = True
    for label, ids in problems:
        if ids:
            ok = False
            print(f"NG {label}: {_sorted_ids(ids)}")
    if report_mixed:
        for tl, landmark, state, states in mixed:
            print(
                f"INFO tlLogic {tl}: landmark {landmark} links differ ({states}) in phase "
                f"{state} -> CARLA shows red"
            )
    print("OK" if ok else "NG")
    return ok


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("net", help="SUMO net (.net.xml)")
    parser.add_argument("map", help="Lanelet2 map with traffic lights (.osm)")
    parser.add_argument("--carla-json", help="--dump-json output of carla_tl_to_lanelet2.py")
    parser.add_argument(
        "--group-id-offset",
        type=int,
        default=0,
        help="--group-id-offset given to carla_tl_to_lanelet2.py (default: 0)",
    )
    parser.add_argument(
        "--report-mixed",
        action="store_true",
        help="list the landmarks the bridge forces to red because their SUMO links differ",
    )
    args = parser.parse_args(argv)
    ok = check(args.net, args.map, args.carla_json, args.group_id_offset, args.report_mixed)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
