import anthropic
import base64
import httpx
import json
import requests
import uuid

# retrieves the first image service of the first painting annotation
def get_image_service(canvas):
  if 'id' in canvas:
    first_painting_anno_page = canvas['items'][0]
    first_painting_anno = first_painting_anno_page['items'][0]
    first_painting_anno_body = first_painting_anno['body']
    # Handle Image API v3 or v2
    return first_painting_anno_body['service'][0].get('id') or first_painting_anno_body['service'][0].get('@id')
  else:
    first_painting_anno = canvas['images'][0]
    first_painting_anno_body = first_painting_anno['resource']
    if isinstance(first_painting_anno_body['service'], list):
      service = first_painting_anno_body['service'][0]
    else:
      service = first_painting_anno_body['service']
    # Handle Image API v3 or v2
    return service.get('@id')

# Create an image URL, scaled to a size appropriate for the AI service used
# Claude requests max of 1568x1568
def get_image(image_service, size="!1568,1568"):
    image_url = f"{image_service}/full/{size}/0/default.jpg"
    media_type = "image/jpeg"
    # encode data
    image_data = base64.standard_b64encode(httpx.get(image_url).content).decode("utf-8")
    return {
        "image_data": image_data,
        "media_type": media_type,
        "image_url": image_url
    }

# Call the Anthropic API
def transcribe_image(image_data, media_type, prompt, system_prompt, key):
    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )
    return message.content[0].text


def create_text_annotation(canvas_id, text, language, motiviation = 'commenting', text_granularity = None):
    create_annotation(canvas_id, text, language, "text/plain", motiviation, text_granularity)

def create_html_annotation(canvas_id, text, language, motiviation = 'commenting', text_granularity = None):
    create_annotation(canvas_id, text, language, "text/html", motiviation, text_granularity)

def create_annotation(canvas_id, text, language, text_format, motivation = 'commenting', text_granularity = None):
    id = f"https://example.org/anno/{uuid.uuid4()}"
    annotation = {
        'id': id,
        'type': 'Annotation',
        'motivation': [motivation],
        'target': canvas_id,
        'body': {
            'id': f"{id}/body",
            'type': 'TextualBody',
            'format': text_format,
            'language': language,
            'value': text
        }
    }
    if text_granularity:
        annotation['textGranularity'] = text_granularity
    return annotation

def create_annotation_page(annotations):
    return {
        'id': f"https://example.org/annopage/{uuid.uuid4()}",
        'type': 'AnnotationPage',
        'items': annotations
    }

# Functions to store and update JSON using the free https://jsonblob.com service
def create_json_location(url, data):
    r = requests.post(
        url,
        data=json.dumps(data),
        headers={'Content-Type': 'application/json'}
    )
    return r, r.headers.get('Location')

def put_manifest_json(url, data):
    """
    Send a JSON payload to the given URL via HTTP PUT.

    Args:
        url (str): The target endpoint.
        data (dict or str): The data to send. If a dict, it will be converted to JSON.

    Returns:
        requests.Response: The HTTP response object returned by the server.
    """
    # Ensure data is JSON string
    if not isinstance(data, str):
        json_data = json.dumps(data)
    else:
        json_data = data

    headers = {"Content-Type": "application/json"}

    # Perform the PUT request
    response = requests.put(url, data=json_data, headers=headers)

    return response
