from ix.api.components.types import NodeTypeField
from ix.runnable.dalle import DalleImage

DALLE_IMAGE_CLASS_PATH = "ix.runnable.dalle.DalleImage"
DALLE_IMAGE = {
    "class_path": DALLE_IMAGE_CLASS_PATH,
    "type": "chain",
    "name": "Dalle Image",
    "description": "Generate an image with Dall-e API",
    "fields": NodeTypeField.get_fields(
        DalleImage,
        include=[
            "input_key",
            "openai_api_key",
            "model",
            "n",
            "size",
            "quality",
            "separator",
            "disable_detail_rewrite",
        ],
        field_options={
            "openai_api_key": {
                "input_type": "secret",
                "secret_key": "OpenAI API",
                "label": "API Key",
                "style": {"width": "100%"},
            },
            "size": {
                "input_type": "select",
                "choices": [
                    {"label": "256x256", "value": "256x256"},
                    {"label": "512x512", "value": "512x512"},
                    {"label": "1024x1024", "value": "1024x1024"},
                    {"label": "1792x1024", "value": "1792x1024"},
                    {"label": "1024x1792", "value": "1024x1792"},
                ],
            },
        },
    ),
}

DALLE = [DALLE_IMAGE]
