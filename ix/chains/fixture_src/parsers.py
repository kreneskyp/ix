from langchain.document_loaders.parsers import LanguageParser
from langchain.text_splitter import Language

from ix.api.components.types import NodeTypeField, parse_enum_choices


LANGUAGE_CHOICES = parse_enum_choices(Language)
LANGUAGE = {
    "name": "language",
    "type": "string",
    "input_type": "select",
    "choices": LANGUAGE_CHOICES,
    "required": True,
    "default": "python",
}

LANGUAGE_PARSER_CLASS_PATH = (
    "langchain.document_loaders.parsers.language.language_parser.LanguageParser"
)
LANGUAGE_PARSER = {
    "class_path": LANGUAGE_PARSER_CLASS_PATH,
    "type": "parser",
    "name": "Language Parser",
    "description": "Parse code for various programming languages.",
    "fields": []
    + NodeTypeField.get_fields(
        LanguageParser.__init__,
        include=["parser_threshold", "language"],
    ),
}

PARSERS = [LANGUAGE_PARSER]

__all__ = ["PARSERS", "LANGUAGE", "LANGUAGE_CHOICES", "LANGUAGE_PARSER_CLASS_PATH"]
