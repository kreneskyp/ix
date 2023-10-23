from langchain import LlamaCpp
from langchain.chat_models import ChatOpenAI
from langchain.llms.base import BaseLLM
from langchain.llms import Ollama
from langchain.llms.fireworks import Fireworks

from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.common import VERBOSE


BASE_LLM_FIELDS = NodeTypeField.get_fields(
    BaseLLM,
    include=["cache", "verbose", "tags", "metadata"],
    field_options={
        "metadata": {
            "type": "dict",
        },
        "cache": {
            "type": "boolean",
        },
        "tags": {
            "type": "list",
        },
    },
)

REQUEST_TIMEOUT = {
    "name": "request_timeout",
    "label": "Timeout (sec)",
    "type": "number",
    "description": "Request Timeout",
    "default": 60,
}

STREAMING = {
    "name": "streaming",
    "type": "boolean",
    "default": True,
}

OPENAI_LLM_CLASS_PATH = "langchain.chat_models.openai.ChatOpenAI"
OPENAI_LLM = {
    "class_path": OPENAI_LLM_CLASS_PATH,
    "type": "llm",
    "name": "OpenAI LLM",
    "description": "OpenAI LLM",
    "fields": [
        {
            "name": "model_name",
            "label": "Model",
            "type": "string",
            "input_type": "select",
            "required": True,
            "description": "OpenAI model",
            "default": "gpt-4-0613",
            "choices": [
                {"label": "GPT-4", "value": "gpt-4"},
                {"label": "GPT-4 (0613)", "value": "gpt-4-0613"},
                {"label": "GPT-3.5 ", "value": "gpt-3.5-turbo"},
                {"label": "GPT-3.5 16k", "value": "gpt-3.5-turbo-16k-0613"},
            ],
        },
    ]
    + NodeTypeField.get_fields(
        ChatOpenAI,
        include=[
            "openai_api_key",
            "openai_organization",
            "openai_api_base",
            "openai_proxy",
            "max_tokens",
        ],
        field_options={
            "openai_api_key": {
                "input_type": "secret",
                "label": "API Key",
                "style": {"width": "100%"},
            },
            "openai_organization": {
                "type": "string",
                "label": "Organization",
                "style": {"width": "100%"},
            },
            "openai_api_base": {
                "type": "string",
                "label": "API Base URL",
                "description": "OpenAI API Base URL",
                "style": {"width": "100%"},
            },
            "openai_proxy": {
                "type": "string",
                "label": "Proxy URL",
                "description": "OpenAI Proxy URL",
                "style": {"width": "100%"},
            },
            "max_tokens": {"type": "string", "default": 500},
        },
    )
    + [
        STREAMING,
        REQUEST_TIMEOUT,
        {
            "name": "max_retries",
            "type": "number",
            "input_type": "slider",
            "description": "Max Retries",
            "default": 6,
            "min": 0,
            "max": 6,
            "step": 1,
        },
        {
            "name": "temperature",
            "type": "number",
            "input_type": "slider",
            "description": "Temperature",
            "default": 0,
            "min": 0,
            "max": 2,
            "step": 0.05,
        },
    ]
    + BASE_LLM_FIELDS,
}

GOOGLE_PALM = {
    "class_path": "langchain.chat_models.google_palm.ChatGooglePalm",
    "type": "llm",
    "name": "Google PaLM",
    "description": "Google PaLM",
    "fields": [
        {
            "name": "model_name",
            "label": "Model",
            "type": "string",
            "input_type": "select",
            "required": True,
            "description": "OpenAI model",
            "default": "gpt-4",
            "choices": [
                {"label": "Bison-001", "value": "models/chat-bison-001"},
            ],
        },
        {
            "name": "google_api_key",
            "label": "API Key",
            "type": "string",
            "description": "Google API key",
            "input_type": "secret",
        },
        {
            "name": "temperature",
            "type": "number",
            "input_type": "slider",
            "description": "Temperature",
            "default": 0,
            "min": 0,
            "max": 2,
            "step": 0.05,
        },
        {
            "name": "top_p",
            "type": "number",
            "input_type": "slider",
            "description": "Top P",
            "default": 0,
            "min": 0,
            "max": 2,
            "step": 0.05,
        },
        {
            "name": "top_k",
            "type": "number",
            "input_type": "slider",
            "description": "Top P",
            "default": 0,
            "min": 0,
            "max": 2,
            "step": 0.05,
        },
        {
            "name": "n",
            "label": "Sample N responses",
            "type": "number",
            "input_type": "slider",
            "description": "Number of responses to sample",
            "default": 1,
            "min": 1,
            "max": 5,
            "step": 1,
        },
    ]
    + BASE_LLM_FIELDS,
}

ANTHROPIC_LLM = {
    "class_path": "langchain.chat_models.anthropic.ChatAnthropic",
    "type": "llm",
    "name": "Anthropic",
    "description": "Anthropic",
    "fields": [
        {
            "name": "temperature",
            "type": "number",
            "input_type": "slider",
            "description": "Temperature",
            "default": 0,
            "min": 0,
            "max": 2,
            "step": 0.05,
        },
        {
            "name": "anthropic_api_key",
            "type": "string",
            "input_type": "secret",
            "style": {"width": "100%"},
            "description": "ANTHROPIC_API_KEY",
        },
        {
            "name": "anthropic_api_url",
            "type": "string",
            "style": {"width": "100%"},
            "description": "API URL",
            "default": "https://api.anthropic.com",
        },
    ]
    + BASE_LLM_FIELDS,
}

LLAMA_CPP_LLM_CLASS_PATH = "langchain.llms.llamacpp.LlamaCpp"
LLAMA_CPP_LLM = {
    "class_path": LLAMA_CPP_LLM_CLASS_PATH,
    "type": "llm",
    "name": "Llama Cpp",
    "description": "Llama Cpp wrapper for llama models",
    "fields": [VERBOSE]
    + NodeTypeField.get_fields(
        LlamaCpp,
        include=[
            "model_path",
            "lora_base",
            "n_ctx",
            "n_parts",
            "seed",
            "f16_kv",
            "logits_all",
            "vocab_only",
            "use_mlock",
            "n_threads",
            "n_batch",
            "n_gpu_layers",
            "suffix",
            "max_tokens",
            "temperature",
            "top_p",
            "logprobs",
            "echo",
            "stop",
            "repeat_penalty",
            "last_n_tokens_size",
            "use_mmap",
            "rope_freq_scale",
            "rope_freq_base",
            # "model_kwargs",
            "streaming",
        ],
    )
    + BASE_LLM_FIELDS,
}

OLLAMA_LLM_CLASS_PATH = "langchain.llms.ollama.Ollama"
OLLAMA_LLM = {
    "class_path": OLLAMA_LLM_CLASS_PATH,
    "type": "llm",
    "name": "Ollama",
    "description": "Ollama server for llama models",
    "fields": [VERBOSE]
    + NodeTypeField.get_fields(
        Ollama,
        include=[
            "base_url",
            "model",
            "mirostat",
            "mirostat_eta",
            "mirostat_tau",
            "num_ctx",
            "num_gpu",
            "num_thread",
            "repeat_last_n",
            "repeat_penalty",
            "temperature",
            "stop",
            "tfs_z",
            "top_p",
        ],
        field_options={
            "temperature": {
                "default": 0.8,
                "input_type": "slider",
                "min": 0,
                "max": 1,
                "step": 0.05,
            },
            "num_gpu": {
                "default": 1,
                "input_type": "slider",
                "min": 0,
                "max": 10,
                "step": 1,
            },
            "top_k": {
                "default": 40,
                "description": "Top K",
                "input_type": "slider",
                "min": 1,
                "max": 100,
                "step": 1,
            },
            "top_p": {
                "default": 0.9,
                "input_type": "slider",
                "min": 0,
                "max": 1,
                "step": 0.05,
            },
            "stop": {
                "style": {"width": "100%"},
            },
        },
    )
    + BASE_LLM_FIELDS,
}


FIREWORKS_FIELDS = NodeTypeField.get_fields(
    Fireworks,
    include=["model", "fireworks_api_key", "max_retries"],
    field_options={
        "model": {
            "style": {"width": "100%"},
        },
        "fireworks_api_key": {
            "input_type": "secret",
            "style": {"width": "100%"},
        },
        "max_retries": {
            "default": 20,
            "input_type": "slider",
            "min": 0,
            "max": 50,
            "step": 1,
        },
    },
) + NodeTypeField.get_fields(
    Fireworks,
    parent="model_kwargs",
    include=[
        "temperature",
        "max_tokens",
        "top_p",
    ],
    field_options={
        "temperature": {
            "default": 0.8,
            "input_type": "slider",
            "min": 0,
            "max": 1,
            "step": 0.05,
        },
        "top_p": {
            "default": 0.9,
            "input_type": "slider",
            "min": 0,
            "max": 1,
            "step": 0.05,
        },
    },
)


FIREWORKS_LLM_CLASS_PATH = "langchain.llms.fireworks.Fireworks"
FIREWORKS_LLM = {
    "class_path": FIREWORKS_LLM_CLASS_PATH,
    "type": "llm",
    "name": "Fireworks.ai",
    "description": "Fireworks.ai LLM",
    "fields": FIREWORKS_FIELDS + BASE_LLM_FIELDS,
}

FIREWORKS_CHAT_LLM_CLASS_PATH = "langchain.chat_models.fireworks.ChatFireworks"
FIREWORKS_CHAT_LLM = {
    "class_path": FIREWORKS_CHAT_LLM_CLASS_PATH,
    "type": "llm",
    "name": "Fireworks.ai (chat)",
    "description": "Fireworks.ai Chat LLM",
    "fields": FIREWORKS_FIELDS + BASE_LLM_FIELDS,
}

LLMS = [
    ANTHROPIC_LLM,
    GOOGLE_PALM,
    LLAMA_CPP_LLM,
    OLLAMA_LLM,
    OPENAI_LLM,
    FIREWORKS_LLM,
    FIREWORKS_CHAT_LLM,
]
