IX_ENV = """
# ==================================================================
# GLOBAL ENVIRONMENT DEFAULTS:
#
# These values are set in the environment of app and worker containers
# They are used by defaults by the corresponding components.
# ==================================================================

# OpenAI is the default LLM used by predefined agents.
OPENAI_API_KEY={OPENAI_API_KEY}

# ==================================================================
# OPTIONAL SETUP:
#
# These values are only required when using the corresponding
# features.
# ==================================================================

# LangSmith logging (requires a LangSmith account)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
# LANGCHAIN_API_KEY=
# LANGCHAIN_PROJECT=default

# llms
GOOGLE_API_KEY=
ANTHROPIC_API_KEY=

# Pinecone
PINECONE_API_KEY=
PINECONE_ENV=

# search
GOOGLE_API_KEY=
GOOGLE_CX_ID=
WOLFRAM_APP_ID=

# METAPHOR
METAPHOR_API_KEY=
"""
