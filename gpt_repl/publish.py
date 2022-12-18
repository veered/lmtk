import requests
import pdb

from .utils.printer import render_markdown_to_html

api_url = "https://chatgpt-share.vercel.app/api/save"
avatar_url = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/4gIoSUNDX1BST0ZJTEUAAQEAAAIYAAAAAAQwAABtbnRyUkdCIFhZWiAAAAAAAAAAAAAAAABhY3NwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQAA9tYAAQAAAADTLQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAlkZXNjAAAA8AAAAHRyWFlaAAABZAAAABRnWFlaAAABeAAAABRiWFlaAAABjAAAABRyVFJDAAABoAAAAChnVFJDAAABoAAAAChiVFJDAAABoAAAACh3dHB0AAAByAAAABRjcHJ0AAAB3AAAADxtbHVjAAAAAAAAAAEAAAAMZW5VUwAAAFgAAAAcAHMAUgBHAEIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAFhZWiAAAAAAAABvogAAOPUAAAOQWFlaIAAAAAAAAGKZAAC3hQAAGNpYWVogAAAAAAAAJKAAAA+EAAC2z3BhcmEAAAAAAAQAAAACZmYAAPKnAAANWQAAE9AAAApbAAAAAAAAAABYWVogAAAAAAAA9tYAAQAAAADTLW1sdWMAAAAAAAAAAQAAAAxlblVTAAAAIAAAABwARwBvAG8AZwBsAGUAIABJAG4AYwAuACAAMgAwADEANv/bAEMAAwICAgICAwICAgMDAwMEBgQEBAQECAYGBQYJCAoKCQgJCQoMDwwKCw4LCQkNEQ0ODxAQERAKDBITEhATDxAQEP/bAEMBAwMDBAMECAQECBALCQsQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEP/AABEIAB4AHgMBIgACEQEDEQH/xAAXAAEBAQEAAAAAAAAAAAAAAAAABQYH/8QAJRAAAQIGAQQDAQAAAAAAAAAAAQACAwQFBhETMQcUFSISIUEy/8QAFQEBAQAAAAAAAAAAAAAAAAAABAj/xAAiEQACAAUEAwEAAAAAAAAAAAABAgADBBEhEjFRYROhscH/2gAMAwEAAhEDEQA/AKaItralu0epdNr5r87J7J+jeM7KNseNW6YcyJ6g/F2WgD2Bx+YUe0lK9ZMMtCAQrNnhVLH0DbuK9qqpKOWJkwG2pVxyzBR7OeoxSIiNCILo3TeZosxYd8WrUrhkaTNVnxnaRJ3YITtMdz35LGOIwMfnJC5yibQVhoZ/m0hsMpBvkMpU7Z2JgldSCuk+EsRlTcW3Vgw3uNwL9RauS3Ja33QGy90Uis7w4k050YiFjH9bIbOc/WM8HhRURHnOjuWRdI4yfuYRKVkQK7ajzj8sI//Z"

class PublishGPT:

  def __init__(self, thread):
    self.thread = thread

  def publish(self):
    conversation_data = self.format_conversation_data(self.thread)
    response = requests.post(
      api_url,
      json=conversation_data,
      headers={
        "origin": "https://chat.openai.com"
      }
    )
    result = response.json()
    return f"https://sharegpt.com/c/{result['id']}"

  def format_conversation_data(self, thread):
    conversation_data = {
      "avatarUrl": avatar_url,
      "items": [],
    }
    for entry in thread["history"]:
      if entry["type"] == "you":
        source = "human"
        value = entry["text"]
      else:
        source = "gpt"
        # value = render_markdown_to_html(entry["text"], title='GPT')
        value = entry["text"]
      conversation_data["items"].append({ "from": source, "value": value })
    return conversation_data
