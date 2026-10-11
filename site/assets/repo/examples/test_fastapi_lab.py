import unittest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from fastapi_lab import create_app

ALPHA = {"Authorization": "Bearer lesson-alpha"}
BETA = {"Authorization": "Bearer lesson-beta"}

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

    def tearDown(self):
        self.client.close()

    def create(self, **kwargs):
        return self.client.post("/v1/tasks", headers=ALPHA,
                                json={"title": "original lab"}, **kwargs)

    def test_missing_identity(self):
        response = self.client.post("/v1/tasks", json={"title": "x"})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def test_strict_and_extra_fields(self):
        for payload in ({"title": "x", "retries": "2"},
                        {"title": "x", "retries": True},
                        {"title": "x", "retries": -1},
                        {"title": "", "retries": 0},
                        {"title": "x", "extra": "secret"}):
            with self.subTest(payload=payload):
                response = self.client.post("/v1/tasks", headers=ALPHA, json=payload)
                self.assertEqual(response.status_code, 422)
                self.assertEqual(response.json()["code"], "invalid_input")
                self.assertNotIn("secret", response.text)

    def test_response_filter_and_background(self):
        response = self.create()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(set(response.json()), {"id", "title", "status"})
        self.assertEqual(len(self.app.state.audit), 1)

    def test_tenant_boundary(self):
        task_id = self.create().json()["id"]
        self.assertEqual(self.client.get(f"/v1/tasks/{task_id}", headers=BETA).status_code, 404)
        self.assertEqual(self.client.get(f"/v1/tasks/{task_id}", headers=ALPHA).status_code, 200)

    def test_idempotency_and_conflict(self):
        headers = ALPHA | {"Idempotency-Key": "k1"}
        first = self.client.post("/v1/tasks", headers=headers, json={"title": "x"})
        again = self.client.post("/v1/tasks", headers=headers, json={"title": "x"})
        self.assertEqual(first.json(), again.json())
        self.assertEqual(len(self.app.state.audit), 1)
        changed = self.client.post("/v1/tasks", headers=headers, json={"title": "y"})
        self.assertEqual(changed.status_code, 409)
        other = self.client.post("/v1/tasks", headers=BETA | {"Idempotency-Key": "k1"},
                                 json={"title": "x"})
        self.assertNotEqual(other.json()["id"], first.json()["id"])

    def test_parallel_same_key_single_process(self):
        def submit(_):
            with TestClient(self.app) as client:
                return client.post("/v1/tasks", headers=ALPHA | {"Idempotency-Key": "parallel"},
                                   json={"title": "same"}).json()["id"]
        with ThreadPoolExecutor(max_workers=4) as pool:
            ids = list(pool.map(submit, range(8)))
        self.assertEqual(len(set(ids)), 1)
        self.assertEqual(len(self.app.state.tasks), 1)

    def test_state_transitions(self):
        task_id = self.create().json()["id"]
        url = f"/v1/tasks/{task_id}"
        self.assertEqual(self.client.patch(url, headers=ALPHA,
                         json={"status": "succeeded"}).status_code, 409)
        for state in ("running", "running", "succeeded"):
            response = self.client.patch(url, headers=ALPHA, json={"status": state})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], state)
        self.assertEqual(self.client.patch(url, headers=ALPHA,
                         json={"status": "running"}).status_code, 409)

    def test_dependency_cache_is_request_local(self):
        for _ in range(2):
            self.assertEqual(self.client.get("/lab/dependency-cache").json(), {"same": True})
        events = self.app.state.resource_events
        self.assertEqual([x[0] for x in events], ["open", "close", "open", "close"])
        self.assertNotEqual(events[0][1], events[2][1])
        self.assertEqual(events[0][1], events[1][1])

    def test_uncached_dependency_and_error_cleanup(self):
        self.assertEqual(self.client.get("/lab/dependency-uncached").json(), {"same": False})
        self.assertEqual(sum(x[0] == "close" for x in self.app.state.resource_events), 2)
        self.assertEqual(self.client.get("/lab/dependency-error").status_code, 409)
        self.assertEqual(sum(x[0] == "close" for x in self.app.state.resource_events), 3)

    def test_upload_count_and_cap(self):
        small = self.client.post("/v1/uploads", headers=ALPHA,
                                 files={"file": ("../ignored.txt", b"abc", "text/plain")})
        self.assertEqual(small.json(), {"bytes": 3})
        large = self.client.post("/v1/uploads", headers=ALPHA,
                                 files={"file": ("large.txt", b"x" * 4097, "text/plain")})
        self.assertEqual(large.status_code, 413)

    def test_cors_preflight(self):
        response = self.client.options("/v1/tasks", headers={
            "Origin": "https://lesson.example", "Access-Control-Request-Method": "POST"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["access-control-allow-origin"], "https://lesson.example")
        rejected = self.client.options("/v1/tasks", headers={
            "Origin": "https://other.example", "Access-Control-Request-Method": "POST"})
        self.assertEqual(rejected.status_code, 400)

    def test_websocket_echo_and_size(self):
        with self.client.websocket_connect("/ws", headers=ALPHA) as socket:
            socket.send_text("hello")
            self.assertEqual(socket.receive_json(), {"echo": "hello"})
            socket.send_text("x" * 129)
            with self.assertRaises(WebSocketDisconnect) as caught:
                socket.receive_json()
            self.assertEqual(caught.exception.code, 1009)

    def test_websocket_unauthorized(self):
        with self.assertRaises(WebSocketDisconnect) as caught:
            with self.client.websocket_connect("/ws"):
                pass
        self.assertEqual(caught.exception.code, 4401)

if __name__ == "__main__":
    unittest.main()
