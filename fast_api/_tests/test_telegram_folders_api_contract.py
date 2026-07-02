import inspect
import unittest

from fastapi.routing import APIRoute

from main import create_fastapi_application


EXPECTED_FOLDER_ENDPOINTS = {
    "/tg_tlt_aggregator_api/get_telegram_folders",
    "/tg_tlt_aggregator_api/get_telegram_folder",
    "/tg_tlt_aggregator_api/get_telegram_folder_dialogs",
    "/tg_tlt_aggregator_api/create_telegram_folder",
    "/tg_tlt_aggregator_api/update_telegram_folder",
    "/tg_tlt_aggregator_api/delete_telegram_folder",
    "/tg_tlt_aggregator_api/reorder_telegram_folders",
    "/tg_tlt_aggregator_api/preview_folder_candidates",
    "/tg_tlt_aggregator_api/resolve_peers_for_folder",
    "/tg_tlt_aggregator_api/get_telegram_archive_dialogs",
    "/tg_tlt_aggregator_api/archive_telegram_peers",
    "/tg_tlt_aggregator_api/unarchive_telegram_peers",
}


class TelegramFoldersAPIContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_fastapi_application().app
        cls.routes = {
            route.path: route for route in cls.app.routes
            if isinstance(route, APIRoute)
        }

    def test_all_folder_endpoints_are_registered(self):
        self.assertTrue(EXPECTED_FOLDER_ENDPOINTS.issubset(self.routes))

    def test_every_folder_endpoint_requires_common_request_models(self):
        for endpoint_path in EXPECTED_FOLDER_ENDPOINTS:
            parameters = inspect.signature(
                self.routes[endpoint_path].endpoint).parameters
            self.assertIn("auth_data", parameters, endpoint_path)
            self.assertIn("web_account_data", parameters, endpoint_path)
            self.assertIn("tlt_config_ref", parameters, endpoint_path)

    def test_every_folder_endpoint_has_response_model(self):
        for endpoint_path in EXPECTED_FOLDER_ENDPOINTS:
            self.assertIsNotNone(
                self.routes[endpoint_path].response_model,
                endpoint_path)

    def test_openapi_generation_includes_all_folder_endpoints(self):
        openapi_paths = self.app.openapi()["paths"]
        self.assertTrue(EXPECTED_FOLDER_ENDPOINTS.issubset(openapi_paths))


if __name__ == "__main__":
    unittest.main()
