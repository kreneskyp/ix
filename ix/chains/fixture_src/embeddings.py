from langchain.embeddings import (
    HuggingFaceInstructEmbeddings,
    HuggingFaceEmbeddings,
    HuggingFaceInferenceAPIEmbeddings,
    HuggingFaceBgeEmbeddings,
    HuggingFaceHubEmbeddings,
)

from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.llm import GOOGLE_API_KEY

OPENAI_EMBEDDINGS_CLASS_PATH = "langchain.embeddings.openai.OpenAIEmbeddings"
OPENAI_EMBEDDINGS = {
    "name": "OpenAI Embeddings",
    "description": "Embeddings from OpenAI's API.",
    "class_path": OPENAI_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "fields": [
        {
            "name": "model",
            "type": "string",
            "default": "text-embedding-ada-002",
            "choices": [
                {"value": "text-embedding-ada-002", "label": "text-embedding-ada-002"},
            ],
            "input_type": "select",
        },
        {
            "name": "allowed_special",
            "type": "list",
        },
        {
            "name": "disallowed_special",
            "type": "list",
            "default": [],
        },
        {
            "name": "chunk_size",
            "type": "int",
            "default": 1000,
        },
        {
            "name": "max_retries",
            "type": "int",
            "default": "6",
            "min": 0,
            "max": 6,
            "step": 1,
            "input_type": "slider",
        },
    ],
}

GOOGLE_PALM_EMBEDDINGS = {
    "class_path": "langchain.embeddings.google_palm.GooglePalmEmbeddings",
    "type": "embeddings",
    "name": "Google PaLM Embeddings",
    "description": "Google PaLM Embeddings",
    "fields": [
        {
            "name": "google_api_key",
            "type": "string",
            "description": "Google PaLM key",
        },
        {
            "name": "model_name",
            "label": "Model",
            "type": "string",
            "default": "models/embedding-gecko-001",
            "description": "Model name to use",
            "choices": [
                {
                    "label": "models/embedding-gecko-001",
                    "value": "models/embedding-gecko-001",
                },
            ],
        },
    ],
}
GOOGLE_GEN_AI_EMBEDDINGS = {
    "class_path": "langchain_google_genai.GoogleGenerativeAIEmbeddings",
    "type": "embeddings",
    "name": "Google Gen AI Embeddings",
    "description": "Google Gen AI Embeddings",
    "fields": [
        GOOGLE_API_KEY,
        {
            "name": "model",
            "type": "string",
            "description": "The name of the embedding model to use. ",
        },
    ],
}

LLAMA_CPP_EMBEDDINGS = {
    "class_path": "langchain.embeddings.llama_cpp.LlamaCppEmbeddings",
    "type": "embeddings",
    "name": "LlamaCpp Embeddings",
    "description": "LlamaCpp Embeddings",
    "fields": [
        {
            "name": "model_path",
            "type": "string",
            "description": "Path to the Llama model",
            "style": {"width": "100%"},
        },
        {
            "name": "n_ctx",
            "type": "number",
            "default": 512,
            "description": "Token context window",
        },
        {
            "name": "n_parts",
            "type": "number",
            "default": -1,
            "description": "Number of parts to split the model into",
        },
        {
            "name": "seed",
            "type": "number",
            "default": -1,
            "description": "Seed. If -1, a random seed is used",
        },
        {
            "name": "f16_kv",
            "type": "boolean",
            "default": False,
            "description": "Use half-precision for key/value cache",
        },
        {
            "name": "logits_all",
            "type": "boolean",
            "default": False,
            "description": "Return logits for all tokens, not just the last token",
        },
        {
            "name": "vocab_only",
            "type": "boolean",
            "default": False,
            "description": "Only load the vocabulary, no weights",
        },
        {
            "name": "use_mlock",
            "type": "boolean",
            "default": False,
            "description": "Force system to keep model in RAM",
        },
        {
            "name": "n_threads",
            "type": "number",
            "description": "Number of threads to use",
        },
        {
            "name": "n_batch",
            "type": "number",
            "default": 8,
            "description": "Number of tokens to process in parallel",
        },
        {
            "name": "n_gpu_layers",
            "type": "number",
            "description": "Number of layers to be loaded into gpu memory",
        },
    ],
}

VERTEXAI_EMBEDDINGS = {
    "class_path": "langchain.embeddings.vertexai.VertexAIEmbeddings",
    "type": "embeddings",
    "name": "VertexAI Embeddings",
    "description": "VertexAI Embeddings",
    "fields": [
        {
            "name": "model_name",
            "label": "Model",
            "type": "string",
            "input_type": "select",
            "default": "textembedding-gecko",
            "description": "Model name to use",
            "choices": [
                {"label": "textembedding-gecko", "value": "textembedding-gecko"},
            ],
        }
    ],
}

HUGGINGFACE_EMBEDDINGS_CLASS_PATH = (
    "langchain.embeddings.huggingface.HuggingFaceEmbeddings"
)
HUGGINGFACE_EMBEDDINGS = {
    "class_path": HUGGINGFACE_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "name": "HuggingFace Embeddings",
    "description": "HuggingFace Embeddings",
    "fields": NodeTypeField.get_fields(
        HuggingFaceEmbeddings,
        include=[
            "model_name",
            "cache_folder",
            "model_kwargs",
            "encode_kwargs",
            "multi_process",
        ],
    ),
}

HUGGINGFACE_INSTRUCT_EMBEDDINGS_CLASS_PATH = (
    "langchain.embeddings.huggingface.HuggingFaceInstructEmbeddings"
)
HUGGINGFACE_INSTRUCT_EMBEDDINGS = {
    "class_path": HUGGINGFACE_INSTRUCT_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "name": "HuggingFace Instruct Embeddings",
    "description": "HuggingFace Instruct Embeddings",
    "fields": NodeTypeField.get_fields(
        HuggingFaceInstructEmbeddings,
        include=[
            "model_name",
            "cache_folder",
            "encode_kwargs",
            "embed_instruction",
            "query_instruction",
        ],
    ),
}

HUGGINGFACE_BGE_EMBEDDINGS_CLASS_PATH = (
    "langchain.embeddings.huggingface.HuggingFaceBgeEmbeddings"
)
HUGGINGFACE_BGE_EMBEDDINGS = {
    "class_path": HUGGINGFACE_BGE_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "name": "HuggingFace BGE Embeddings",
    "description": "HuggingFace BGE Embeddings",
    "fields": NodeTypeField.get_fields(
        HuggingFaceBgeEmbeddings,
        include=[
            "model_name",
            "cache_folder",
            "model_kwargs",
            "encode_kwargs",
            "query_instruction",
        ],
    ),
}


HUGGINGFACE_INFERENCE_API_EMBEDDINGS_CLASS_PATH = (
    "langchain.embeddings.huggingface.HuggingFaceInferenceAPIEmbeddings"
)
HUGGINGFACE_INFERENCE_API_EMBEDDINGS = {
    "class_path": HUGGINGFACE_INFERENCE_API_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "name": "HuggingFace Inference API Embeddings",
    "description": "HuggingFace Inference API Embeddings",
    "fields": NodeTypeField.get_fields(
        HuggingFaceInferenceAPIEmbeddings,
        include=["api_key", "model_name"],
        field_options={
            "api_key": {
                "input_type": "secret",
            }
        },
    ),
}


HUGGINGFACE_HUB_EMBEDDINGS_CLASS_PATH = (
    "langchain.embeddings.huggingface_hub.HuggingFaceHubEmbeddings"
)
HUGGINGFACE_HUB_EMBEDDINGS = {
    "class_path": HUGGINGFACE_HUB_EMBEDDINGS_CLASS_PATH,
    "type": "embeddings",
    "name": "HuggingFace Hub Embeddings",
    "description": "HuggingFace Hub Embeddings",
    "fields": NodeTypeField.get_fields(
        HuggingFaceHubEmbeddings,
        include=["repo_id", "huggingfacehub_api_token", "task", "model_kwargs"],
        field_options={
            "huggingfacehub_api_token": {
                "input_type": "secret",
            }
        },
    ),
}


MOSAICML_INSTRUCTOR_EMBEDDINGS = {
    "class_path": "langchain.embeddings.mosaicml.MosaicMLInstructorEmbeddings",
    "type": "embeddings",
    "name": "MosaicML Instructor Embeddings",
    "description": "MosaicML Instructor Embeddings",
    "fields": [
        {
            "name": "endpoint_url",
            "type": "string",
            "default": "https://models.hosted-on.mosaicml.hosting/instructor-xl/v1/predict",
            "description": "Endpoint URL to use",
            "style": {"width": "100%"},
        },
        {
            "name": "embed_instruction",
            "type": "string",
            "default": "Represent the document for retrieval: ",
            "description": "Instruction used to embed documents",
        },
        {
            "name": "query_instruction",
            "type": "string",
            "default": "Represent the question for retrieving supporting documents: ",
            "description": "Instruction used to embed the query",
        },
        {
            "name": "retry_sleep",
            "type": "number",
            "default": 1.0,
            "description": "How long to try sleeping for if a rate limit is encountered",
        },
        {
            "name": "mosaicml_api_token",
            "type": "string",
            "input_type": "secret",
            "secret_key": "MosaicML API",
            "style": {"width": "100%"},
        },
    ],
}

EMBEDDINGS = [
    OPENAI_EMBEDDINGS,
    GOOGLE_GEN_AI_EMBEDDINGS,
    GOOGLE_PALM_EMBEDDINGS,
    LLAMA_CPP_EMBEDDINGS,
    VERTEXAI_EMBEDDINGS,
    HUGGINGFACE_EMBEDDINGS,
    HUGGINGFACE_INSTRUCT_EMBEDDINGS,
    HUGGINGFACE_BGE_EMBEDDINGS,
    HUGGINGFACE_INFERENCE_API_EMBEDDINGS,
    HUGGINGFACE_HUB_EMBEDDINGS,
    MOSAICML_INSTRUCTOR_EMBEDDINGS,
]
