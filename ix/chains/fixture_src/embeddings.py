OPENAI_EMBEDDINGS = {
    "name": "OpenAI Embeddings",
    "description": "Embeddings from OpenAI's API.",
    "class_path": "langchain.embeddings.openai.OpenAIEmbeddings",
    "type": "embeddings",
    "fields": [
        {
            "name": "model",
            "type": "string",
            "default": "text-embedding-ada-002",
            "choices": [
                {"name": "text-embedding-ada-002", "label": "text-embedding-ada-002"},
            ],
        }
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
            "description": "Google API key",
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

HUGGINGFACE_EMBEDDINGS = {
    "class_path": "langchain.embeddings.huggingface.HuggingFaceEmbeddings",
    "type": "embeddings",
    "name": "HuggingFace Embeddings",
    "description": "HuggingFace Embeddings",
    "fields": [
        {
            "name": "model_name",
            "label": "Model",
            "type": "string",
            "default": "sentence-transformers/all-mpnet-base-v2",
            "description": "Model name to use",
            "choices": [
                {
                    "label": "all-mpnet-base-v2",
                    "value": "sentence-transformers/all-mpnet-base-v2",
                },
            ],
            "style": {"width": "100%"},
        },
        {
            "name": "cache_folder",
            "type": "string",
            "description": "Path to store models",
        },
        {
            "name": "model_kwargs",
            "type": "dictionary",
            "description": "Key word arguments to pass to the model",
        },
        {
            "name": "encode_kwargs",
            "type": "dictionary",
            "description": "Key word arguments to pass when calling the `encode` method of the model",
        },
    ],
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
            "description": "MosaicML API token",
            "style": {"width": "100%"},
        },
    ],
}
