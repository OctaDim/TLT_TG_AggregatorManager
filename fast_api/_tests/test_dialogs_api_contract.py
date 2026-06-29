import os
import unittest


APP_DIR = os.path.dirname(os.path.dirname(__file__))
MAIN_PATH = os.path.join(os.path.dirname(APP_DIR), "main.py")


def read_file(file_path):
    with open(file_path, "r") as file_obj:
        return file_obj.read()


class DialogsApiContractTests(unittest.TestCase):
    def test_main_registers_dialog_routes(self):
        main_source = read_file(MAIN_PATH)
        self.assertIn("rtr_get_dialogs_by_configs", main_source)
        self.assertIn("rtr_get_dialog_messages_live", main_source)
        self.assertIn("rtr_send_dialog_message", main_source)
        self.assertIn("rtr_send_dialog_files", main_source)

    def test_dialog_routes_exist(self):
        router_paths = [
            os.path.join(APP_DIR, "app_dialogs_by_configs", "router_dialogs_by_configs.py"),
            os.path.join(APP_DIR, "app_dialog_messages_live", "router_dialog_messages_live.py"),
            os.path.join(APP_DIR, "app_send_dialog_message", "router_send_dialog_message.py"),
            os.path.join(APP_DIR, "app_send_dialog_files", "router_send_dialog_files.py"),
        ]
        for cur_path in router_paths:
            self.assertTrue(os.path.exists(cur_path), cur_path)

    def test_common_helper_supports_peer_storage_type(self):
        helper_source = read_file(
            os.path.join(APP_DIR, "app_dialogs_common", "helper_dialogs_common.py"))
        self.assertIn("SUPPORTED_PEER_STORAGE_TYPES", helper_source)
        self.assertIn("serialize_dialog_item", helper_source)
        self.assertIn("serialize_live_message", helper_source)


if __name__ == "__main__":
    unittest.main()

