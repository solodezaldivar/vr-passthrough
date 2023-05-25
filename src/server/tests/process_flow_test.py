# import unittest
# import os
# import sys
# import json
#
# # Working directory is your masterproject folder -> parent folder of vr-passthrough
# server_path = f"{os.getcwd()}/vr-passthrough/src/server"
# json_output_filename = f"{server_path}/json_data.json"
#
# sys.path.insert(
#     0,
#     server_path
# )
#
# import socket_server
#
# class ProccessTest(unittest.TestCase):
#
#     def setUp(self) -> None:
#         initial_load = {
#             "initial": "entry"
#         }
#         with open(json_output_filename, "w") as f:
#             json.dump(initial_load, f)
#         return super().setUp()
#
#     def test_initial_setup_for_active_source(self):
#
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.3,
#                 "x": 0.234,
#                 "y": 0.322,
#                 "z": -0.234
#             }
#             ]
#         }
#
#         socket_server.process(json.dumps(data))
#         active_source = socket_server.active_source
#
#         with open(json_output_filename) as f:
#             output_json = json.load(f)
#
#         self.assertIsNotNone(active_source)
#         self.assertNotEqual(active_source["id"], 0)
#         self.assertIsNotNone(output_json.get("sounds"))
#
#     def test_activity_at_threshold_returns_null(self):
#
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.3,
#                 "x": 0.234,
#                 "y": 0.322,
#                 "z": -0.234
#             }
#             ]
#         }
#         socket_server.process(json.dumps(data))
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.2,
#                 "x": 0.255,
#                 "y": 0.212,
#                 "z": -0.434
#             }
#             ]
#         }
#         socket_server.process(json.dumps(data))
#         active_source = socket_server.active_source
#         with open(json_output_filename) as f:
#             output_json = json.load(f)
#         self.assertIsNotNone(active_source)
#         self.assertIsNone(output_json["sounds"][0]["direction"].get("x"))
#         self.assertIsNone(output_json["sounds"][0]["direction"].get("y"))
#         self.assertIsNone(output_json["sounds"][0]["direction"].get("z"))
#
#     def test_activity_above_threshold_after_it_was_below(self):
#
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.3,
#                 "x": 0.234,
#                 "y": 0.322,
#                 "z": -0.234
#             }
#             ]
#         }
#
#         socket_server.process(json.dumps(data))
#
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.2,
#                 "x": 0.255,
#                 "y": 0.212,
#                 "z": -0.434
#             }
#             ]
#         }
#
#         socket_server.process(json.dumps(data))
#
#         x = 0.199
#         y = -0.213
#         z = 1.577
#
#         data = {
#             "src": [{
#                 "id": 1,
#                 "activity": 0.3,
#                 "x": x,
#                 "y": y,
#                 "z": z
#             }
#             ]
#         }
#
#         socket_server.process(json.dumps(data))
#         active_source = socket_server.active_source
#
#         with open(json_output_filename) as f:
#             output_json = json.load(f)
#
#         self.assertIsNotNone(active_source)
#         self.assertEqual(output_json["sounds"][0]["direction"].get("x"), x)
#         self.assertEqual(output_json["sounds"][0]["direction"].get("y"), y)
#         self.assertEqual(output_json["sounds"][0]["direction"].get("z"), z)
#
#
# if __name__ == '__main__':
#     unittest.main()
