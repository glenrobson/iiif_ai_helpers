import unittest
from iiif_ai_helpers.utils import *
import json
import base64
from unittest.mock import patch, MagicMock

class TestManifests(unittest.TestCase):

    def setUp(self):
        pass

    def test_yale(self):
        with open("tests/fixtures/yale_15238597.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)

        canvas = manifest['items'][0]
        image_service = get_image_service(canvas)
        self.assertEqual(image_service, "https://collections.library.yale.edu/iiif/2/15239177")


    def test_v2(self):
        with open("tests/fixtures/v2_1362421.json", "r", encoding="utf-8") as f:
            manifest = json.load(f)

        canvas = manifest['sequences'][0]['canvases'][0]
        image_service = get_image_service(canvas)

        self.assertEqual(image_service, "https://damsssl.llgc.org.uk/iiif/2.0/image/1362422")

    def test_get_image(self):
        service = "https://example.org/iiif/2/abc123"
        size = "!800,800"
        expected_url = f"{service}/full/{size}/0/default.jpg"
        fake_bytes = b"fake-jpeg-binary"

        with patch("iiif_ai_helpers.utils.httpx.get") as mock_get:  # patch where it's *imported*
            mock_get.return_value.content = fake_bytes

            result = get_image(service, size=size)

        self.assertEqual(result["image_url"], expected_url)
        self.assertEqual(result["media_type"], "image/jpeg")
        self.assertEqual(result["image_data"], base64.standard_b64encode(fake_bytes).decode("utf-8"))
        mock_get.assert_called_once_with(expected_url)

    def test_create_annotation(self):
        annotation = create_text_annotation("https://example.com/canvas/1", "text", "cy", motiviation='transcribing', text_granularity = "word")    

        self.assertEqual(annotation["target"], "https://example.com/canvas/1")
        self.assertTrue("body" in annotation)
        body = annotation["body"]
        self.assertEqual(body["value"], "text")
        self.assertEqual(body["language"], "cy")
        self.assertEqual(annotation["motivation"][0],"transcribing")
        self.assertEqual(annotation["textGranularity"], "word")

    def test_create_json(self):
        url = "https://api.jsonblob.com/"
        data = {}

        # Prepare a mock response object
        mock_response = MagicMock()
        mock_response.headers = {"Location": "/019a777f-74b2-7840-840c-f32819f9baca"}

        with patch("iiif_ai_helpers.utils.requests.post", return_value=mock_response) as mock_post:
            response, location = create_json_location(url, data)

        # --- Assertions ---
        mock_post.assert_called_once_with(
            url,
            data=json.dumps(data),
            headers={"Content-Type": "application/json"}
        )
        
        self.assertEqual(location, "/019a777f-74b2-7840-840c-f32819f9baca")

    def test_update_json(self):
        url = "https://api.jsonblob.com/test"
        data = {}

        # Prepare a mock response object
        mock_response = MagicMock()
        mock_response.headers = {"Location": "/019a777f-74b2-7840-840c-f32819f9baca"}
        mock_response.json = {}
        mock_response.status_code = 200

        with patch("iiif_ai_helpers.utils.requests.put", return_value=mock_response) as mock_post:
            response = put_manifest_json(url, data)
        
        self.assertEqual(response.status_code, 200)        