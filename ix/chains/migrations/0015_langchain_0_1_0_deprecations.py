# Generated by Django 4.2.6 on 2024-01-15 17:29

from django.db import migrations

from ix.utils.django.migrations import UpdateComponentClassPath


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0014_nodetype_context"),
    ]

    operations = [
        UpdateComponentClassPath(
            [
                (
                    "langchain.chat_models.ChatOpenAI",
                    "langchain_community.chat_models.ChatOpenAI",
                ),
                (
                    "langchain.document_loaders.base.BaseLoader",
                    "langchain_community.document_loaders.base.BaseLoader",
                ),
                (
                    "langchain.vectorstores.redis.base.RedisVectorStoreRetriever",
                    "langchain_community.vectorstores.redis.base.RedisVectorStoreRetriever",
                ),
                (
                    "langchain.document_loaders.generic.GenericLoader",
                    "langchain_community.document_loaders.generic.GenericLoader",
                ),
                (
                    "langchain.document_loaders.web_base.WebBaseLoader",
                    "langchain_community.document_loaders.web_base.WebBaseLoader",
                ),
                (
                    "langchain.document_loaders.csv_loader.CSVLoader",
                    "langchain_community.document_loaders.csv_loader.CSVLoader",
                ),
                (
                    "langchain.document_loaders.JSONLoader",
                    "langchain_community.document_loaders.JSONLoader",
                ),
                (
                    "langchain.document_loaders.PyPDFLoader",
                    "langchain_community.document_loaders.PyPDFLoader",
                ),
                (
                    "langchain.document_loaders.BSHTMLLoader",
                    "langchain_community.document_loaders.BSHTMLLoader",
                ),
                (
                    "langchain.embeddings.openai.OpenAIEmbeddings",
                    "langchain_community.embeddings.openai.OpenAIEmbeddings",
                ),
                (
                    "langchain.embeddings.huggingface.HuggingFaceEmbeddings",
                    "langchain_community.embeddings.huggingface.HuggingFaceEmbeddings",
                ),
                (
                    "langchain.embeddings.huggingface.HuggingFaceInstructEmbeddings",
                    "langchain_community.embeddings.huggingface.HuggingFaceInstructEmbeddings",
                ),
                (
                    "langchain.embeddings.huggingface.HuggingFaceBgeEmbeddings",
                    "langchain_community.embeddings.huggingface.HuggingFaceBgeEmbeddings",
                ),
                (
                    "langchain.embeddings.huggingface.HuggingFaceInferenceAPIEmbeddings",
                    "langchain_community.embeddings.huggingface.HuggingFaceInferenceAPIEmbeddings",
                ),
                (
                    "langchain.embeddings.huggingface_hub.HuggingFaceHubEmbeddings",
                    "langchain_community.embeddings.huggingface_hub.HuggingFaceHubEmbeddings",
                ),
                (
                    "langchain.embeddings.mosaicml.MosaicMLInstructorEmbeddings",
                    "langchain_community.embeddings.mosaicml.MosaicMLInstructorEmbeddings",
                ),
                (
                    "langchain.embeddings.google_palm.GooglePalmEmbeddings",
                    "langchain_community.embeddings.google_palm.GooglePalmEmbeddings",
                ),
                (
                    "langchain.embeddings.llama_cpp.LlamaCppEmbeddings",
                    "langchain_community.embeddings.llama_cpp.LlamaCppEmbeddings",
                ),
                (
                    "langchain.embeddings.vertexai.VertexAIEmbeddings",
                    "langchain_community.embeddings.vertexai.VertexAIEmbeddings",
                ),
                (
                    "langchain.llms.ollama.Ollama",
                    "langchain_community.llms.ollama.Ollama",
                ),
                (
                    "langchain.schema.vectorstore.VectorStoreRetriever",
                    "langchain_core.vectorstores.VectorStoreRetriever",
                ),
                (
                    "langchain.document_loaders.parsers.language.language_parser.LanguageParser",
                    "langchain_community.document_loaders.parsers.language.language_parser.LanguageParser",
                ),
                (
                    "langchain.agents.agent_toolkits.file_management.toolkit.FileManagementToolkit",
                    "langchain_community.agent_toolkits.FileManagementToolkit",
                ),
            ]
        )
    ]
