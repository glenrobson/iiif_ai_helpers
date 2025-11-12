import unittest
from iiif_ai_helpers.utils import *
import json
import base64
from unittest.mock import patch

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