# iiif-ai-helpers

To import this code into a Jupiter Notebook you can do the following:

```
# Import helper code
import os
if not os.path.exists("iiif_ai_helpers"):
  !git clone https://github.com/glenrobson/iiif_ai_helpers.git

import sys
sys.path.append("/content/iiif_ai_helpers")

from iiif_ai_helpers.utils import *

# Could make this more explicit:
# from iiif_ai_helpers.utils import get_image_service
```

Then call it like:

```
import json
import requests

url = "https://damsssl.llgc.org.uk/iiif/2.0/1362421/manifest.json"
response = requests.get(url)
manifest = response.json()

# print the image service for the first canvas
if 'id' in manifest:
  canvas = manifest['items'][0]
  image_service = get_image_service(canvas)
else:
  canvas = manifest['sequences'][0]['canvases'][0]
  image_service = get_image_service(canvas)

print(image_service)
```
