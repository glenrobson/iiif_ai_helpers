import unittest
from iiif_ai_helpers.utils import *
import json

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

