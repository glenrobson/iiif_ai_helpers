import anthropic
import base64
import httpx
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
def get_image(image_service):
    image_url = f"{image_service}/full/!1568,1568/0/default.jpg"
    media_type = "image/jpeg"
    # encode data
    image_data = base64.standard_b64encode(httpx.get(image_url).content).decode("utf-8")
    return {
        "image_data": image_data,
        "media_type": media_type,
        "image_url": image_url
    }

# Call the Anthropic API
def transcribe_image(image_data, media_type, key):
    client = anthropic.Anthropic(api_key=key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
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
                        "text": "Transcribe the text of the document in this image.  Do not describe the document or provide commentary, just the transcription."
                    }
                ],
            }
        ],
    )
    return message.content[0].text