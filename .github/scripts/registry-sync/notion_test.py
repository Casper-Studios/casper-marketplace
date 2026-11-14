import io
import json
import unittest
import urllib.error
from email.message import Message

import notion
from notion import Notion, NotionError, Page


class Response:
    def __init__(self, status, body):
        self.status = status
        self._body = json.dumps(body).encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def http_error(status, body=None, retry_after=None):
    headers = Message()
    if retry_after is not None:
        headers["Retry-After"] = str(retry_after)
    return urllib.error.HTTPError("https://api.notion.com/x", status, "err", headers, io.BytesIO(json.dumps(body or {}).encode()))


class FakeOpener:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, request, timeout=None):
        self.calls.append((request.get_method(), request.full_url, request.data, dict(request.header_items())))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def client(*responses, dry_run=False, log=None):
    opener = FakeOpener(*responses)
    sleeps = []
    api = Notion("tok", dry_run=dry_run, opener=opener, sleep=sleeps.append, log=log or (lambda s: None))
    return api, opener, sleeps


class RequestTest(unittest.TestCase):
    def test_headers_and_body(self):
        api, opener, _ = client(Response(200, {"ok": True}))
        status, payload = api.request("POST", "/v1/x", {"a": 1})
        self.assertEqual((status, payload), (200, {"ok": True}))
        method, url, data, headers = opener.calls[0]
        self.assertEqual((method, url), ("POST", "https://api.notion.com/v1/x"))
        self.assertEqual(json.loads(data), {"a": 1})
        self.assertEqual(headers["Authorization"], "Bearer tok")
        self.assertEqual(headers["Notion-version"], notion.VERSION)

    def test_retries_on_429_with_retry_after(self):
        api, opener, sleeps = client(http_error(429, retry_after=3), Response(200, {}))
        self.assertEqual(api.request("GET", "/v1/x")[0], 200)
        self.assertEqual(sleeps, [3.0])
        self.assertEqual(len(opener.calls), 2)

    def test_retries_on_5xx_with_backoff(self):
        api, _, sleeps = client(http_error(502), http_error(503), Response(200, {}))
        self.assertEqual(api.request("GET", "/v1/x")[0], 200)
        self.assertEqual(sleeps, [1.0, 2.0])

    def test_gives_up_after_six_tries(self):
        api, opener, _ = client(*[http_error(429, {"message": "slow down"}, retry_after=1)] * 6)
        with self.assertRaises(NotionError) as caught:
            api.request("GET", "/v1/x")
        self.assertEqual(len(opener.calls), 6)
        self.assertIn("gave up after 6 tries", str(caught.exception))

    def test_4xx_is_returned_not_retried(self):
        api, opener, _ = client(http_error(404, {"message": "Could not find page"}))
        self.assertEqual(api.request("GET", "/v1/pages/abc"), (404, {"message": "Could not find page"}))
        self.assertEqual(len(opener.calls), 1)

    def test_network_error_is_retried(self):
        api, _, sleeps = client(urllib.error.URLError("boom"), Response(200, {}))
        self.assertEqual(api.request("GET", "/v1/x")[0], 200)
        self.assertEqual(sleeps, [1.0])

    def test_missing_token(self):
        with self.assertRaises(NotionError):
            Notion("")


class ReadTest(unittest.TestCase):
    def test_get_page_404_is_none(self):
        api, _, _ = client(http_error(404))
        self.assertIsNone(api.get_page("3c8e373e-28c6-8186-8974-ec9caf2865ae"))

    def test_get_page_strips_dashes(self):
        api, opener, _ = client(Response(200, {"id": "x"}))
        api.get_page("3c8e373e-28c6-8186-8974-ec9caf2865ae")
        self.assertTrue(opener.calls[0][1].endswith("/v1/pages/3c8e373e28c681868974ec9caf2865ae"))

    def test_query_by_name(self):
        api, opener, _ = client(Response(200, {"results": [{"id": "r1"}]}))
        rows = api.query_by_name("ds", "a-skill")
        self.assertEqual([row.id for row in rows], ["r1"])
        self.assertEqual(json.loads(opener.calls[0][2]), {"filter": {"property": "Name", "title": {"equals": "a-skill"}}})

    def test_query_404_explains_connection(self):
        api, _, _ = client(http_error(404, {"message": "object_not_found"}))
        with self.assertRaises(NotionError) as caught:
            api.query_by_name("ds", "x")
        self.assertIn("Connect the registry-sync connection", str(caught.exception))

    def test_query_all_paginates(self):
        api, opener, _ = client(
            Response(200, {"results": [{"id": "1"}], "has_more": True, "next_cursor": "c2"}),
            Response(200, {"results": [{"id": "2"}], "has_more": False}),
        )
        self.assertEqual([p.id for p in api.query_all("ds")], ["1", "2"])
        self.assertEqual(json.loads(opener.calls[0][2]), {"page_size": 100})
        self.assertEqual(json.loads(opener.calls[1][2]), {"page_size": 100, "start_cursor": "c2"})

    def test_has_content(self):
        api, opener, _ = client(Response(200, {"results": [{"object": "block"}]}), Response(200, {"results": []}))
        self.assertTrue(api.has_content("3c8e373e-28c6-8186-8974-ec9caf2865ae"))
        self.assertFalse(api.has_content("abc"))
        self.assertTrue(opener.calls[0][1].endswith("/v1/blocks/3c8e373e28c681868974ec9caf2865ae/children?page_size=1"))

    def test_list_users_paginates(self):
        api, opener, _ = client(
            Response(200, {"results": [{"id": "1"}], "has_more": True, "next_cursor": "c2"}),
            Response(200, {"results": [{"id": "2"}], "has_more": False}),
        )
        self.assertEqual([u.id for u in api.list_users()], ["1", "2"])
        self.assertIn("start_cursor=c2", opener.calls[1][1])

    def test_find_user_exact_case_insensitive_person_only(self):
        users = [
            {"id": "bot", "type": "bot", "name": "Brian Metrillo"},
            {"id": "p1", "type": "person", "name": "brian metrillo"},
            {"id": "p2", "type": "person", "name": "Brian"},
        ]
        api, _, _ = client(Response(200, {"results": users, "has_more": False}))
        self.assertEqual(api.find_user("Brian Metrillo"), "p1")

    def test_find_user_ambiguous_is_none(self):
        users = [{"id": "p1", "type": "person", "name": "Sam"}, {"id": "p2", "type": "person", "name": "sam"}]
        api, _, _ = client(Response(200, {"results": users, "has_more": False}))
        self.assertIsNone(api.find_user("Sam"))

    def test_find_user_empty_name(self):
        api, opener, _ = client()
        self.assertIsNone(api.find_user(None))
        self.assertEqual(opener.calls, [])


class WriteTest(unittest.TestCase):
    def test_dry_run_prints_and_sends_nothing(self):
        lines = []
        api, opener, _ = client(dry_run=True, log=lines.append)
        page = api.create_page("ds", {"Name": notion.title("x")})
        self.assertEqual(opener.calls, [])
        self.assertEqual(page.id, notion.DRY_RUN_ID)
        self.assertEqual(lines[0], "DRY RUN POST https://api.notion.com/v1/pages")
        self.assertIn('"data_source_id": "ds"', lines[1])
        api.update_page("3c8e373e-28c6-8186-8974-ec9caf2865ae", {"Status": notion.status("Beta")})
        self.assertEqual(lines[2], "DRY RUN PATCH https://api.notion.com/v1/pages/3c8e373e28c681868974ec9caf2865ae")

    def test_append_blocks(self):
        api, opener, _ = client(Response(200, {"results": []}))
        api.append_blocks("abc", [{"object": "block"}])
        method, url, data, _ = opener.calls[0]
        self.assertEqual((method, url), ("PATCH", "https://api.notion.com/v1/blocks/abc/children"))
        self.assertEqual(json.loads(data), {"children": [{"object": "block"}]})

    def test_append_blocks_dry_run(self):
        lines = []
        api, opener, _ = client(dry_run=True, log=lines.append)
        api.append_blocks("abc", [])
        self.assertEqual(opener.calls, [])
        self.assertEqual(lines[0], "DRY RUN PATCH https://api.notion.com/v1/blocks/abc/children")

    def test_create_page_live(self):
        api, opener, _ = client(Response(200, {"id": "new", "url": "https://www.notion.so/new"}))
        page = api.create_page("ds", {"Name": notion.title("x")})
        self.assertEqual((page.id, page.link), ("new", "https://www.notion.so/new"))
        body = json.loads(opener.calls[0][2])
        self.assertEqual(body["parent"], {"type": "data_source_id", "data_source_id": "ds"})

    def test_unexpected_shape_raises(self):
        api, _, _ = client(Response(200, {"results": "nope"}))
        with self.assertRaises(NotionError) as caught:
            api.query_by_name("ds", "x")
        self.assertIn("unexpected shape", str(caught.exception))

    def test_update_page_400_raises(self):
        api, _, _ = client(http_error(400, {"message": "bad property"}))
        with self.assertRaises(NotionError) as caught:
            api.update_page("abc", {})
        self.assertEqual(caught.exception.status, 400)


class ShapeTest(unittest.TestCase):
    def test_property_shapes(self):
        self.assertEqual(notion.title("n"), {"title": [{"text": {"content": "n"}}]})
        self.assertEqual(notion.status("Beta"), {"status": {"name": "Beta"}})
        self.assertEqual(notion.select("HR"), {"select": {"name": "HR"}})
        self.assertEqual(notion.people("u"), {"people": [{"object": "user", "id": "u"}]})

    def test_long_text_is_chunked(self):
        parts = notion._chunks("x" * 4500)
        self.assertEqual([len(p["text"]["content"]) for p in parts], [2000, 2000, 500])
        self.assertEqual(notion.rich_text("x" * 4500), {"rich_text": parts})

    def test_page_readers(self):
        page = Page.model_validate({
            "id": "3c8e373e-28c6-8186-8974-ec9caf2865ae",
            "url": "https://www.notion.so/p",
            "archived": False,
            "in_trash": True,
            "parent": {"type": "data_source_id", "data_source_id": "39ce373e-28c6-806c-a81c-000b11e50a5a"},
            "properties": {
                "Name": {"title": [{"plain_text": "summarize-"}, {"plain_text": "standup-notes"}]},
                "Status": {"status": {"name": "For Review"}},
                "Plugin": {"select": {"name": "x"}},
                "Marketplace": {"select": {"name": "Secret Sauce"}},
                "User Group": {"select": None},
                "created_time": "ignored",
            },
        })
        self.assertEqual(page.title, "summarize-standup-notes")
        self.assertEqual(page.status, "For Review")
        self.assertEqual((page.plugin, page.marketplace, page.user_group), ("x", "Secret Sauce", None))
        self.assertTrue(page.in_trash)
        self.assertEqual(page.parent_id, "39ce373e28c6806ca81c000b11e50a5a")
        self.assertEqual(page.link, "https://www.notion.so/p")

    def test_page_with_little_in_it(self):
        page = Page.model_validate({"id": "abc", "properties": {"Status": {"status": None}}})
        self.assertEqual((page.title, page.status, page.parent_id), ("", None, None))
        self.assertEqual(page.link, "https://www.notion.so/abc")


if __name__ == "__main__":
    unittest.main()
