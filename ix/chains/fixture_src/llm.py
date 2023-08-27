from langchain import LlamaCpp

from ix.api.chains.types import NodeTypeField

OPENAI_LLM = {
    "class_path": "langchain.chat_models.openai.ChatOpenAI",
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
        {
            "name": "request_timeout",
            "label": "Timeout (sec)",
            "type": "number",
            "description": "Request Timeout",
            "default": 60,
        },
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
        {
            "name": "max_tokens",
            "type": "number",
            "default": 256,
        },
        {
            "name": "verbose",
            "type": "boolean",
            "default": False,
        },
        {
            "name": "streaming",
            "type": "boolean",
            "default": True,
        },
    ],
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
        {
            "name": "verbose",
            "type": "boolean",
            "default": False,
        },
    ],
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
    ],
}

LLAMA_CPP_LLM_CLASS_PATH = "langchain.llms.llamacpp.LlamaCpp"
LLAMA_CPP_LLM = {
    "class_path": LLAMA_CPP_LLM_CLASS_PATH,
    "type": "llm",
    "name": "Llama Cpp",
    "description": "Llama Cpp wrapper for llama models",
    "fields": NodeTypeField.get_fields(
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
            "verbose",
        ],
    ),
}


LLMS = [ANTHROPIC_LLM, GOOGLE_PALM, LLAMA_CPP_LLM, OPENAI_LLM]
