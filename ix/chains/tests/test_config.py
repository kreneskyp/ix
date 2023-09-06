from abc import ABC
from enum import Enum
from typing import Literal, Optional

import pytest
from pydantic import BaseModel
from ix.api.components.types import NodeTypeField, InputType


class ChoicesEnum(str, Enum):
    CPP = "cpp"
    GO = "go"


class TestModel(BaseModel):
    field1: str
    field2: int
    field3: bool = False
    literal: Literal["foo", "bar"] = "bar"
    optional: Optional[str] = None
    choices_enum: ChoicesEnum

    @classmethod
    def loader(
        cls,
        field1: str,
        field2: int,
        choices_enum: ChoicesEnum,
        field3: bool = False,
        literal: Literal["foo", "bar"] = "bar",
        optional: Optional[str] = None,
    ):
        pass


class TestABC(ABC):
    field1: str
    field2: int
    field3: bool = False
    literal: Literal["foo", "bar"] = "bar"
    optional: Optional[str] = None
    choices_enum: ChoicesEnum


@pytest.fixture
def field_overrides():
    return {
        "field1": {
            "name": "field1",
            "label": "Custom Field 1",
            "type": "str",
            "default": "custom_default",
        }
    }


@pytest.fixture
def valid_field_config():
    return {
        "name": "test_field",
        "label": "Test Field",
        "type": "int",
        "default": 0,
        "required": True,
    }


class TestFieldConfig:
    def test_slider_without_min_max(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SLIDER
        with pytest.raises(
            ValueError, match="'min' and 'max' are required for 'SLIDER' input type."
        ):
            NodeTypeField(**valid_field_config)

    def test_select_without_choices(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SELECT
        with pytest.raises(
            ValueError, match="'choices' are required for 'SELECT' input type."
        ):
            NodeTypeField(**valid_field_config)

    def test_slider_without_step(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SLIDER
        valid_field_config["min"] = 0
        valid_field_config["max"] = 100
        with pytest.raises(
            ValueError, match="'step' is required for 'SLIDER' input type."
        ):
            NodeTypeField(**valid_field_config)


class GetFieldsBase:
    """Base for common tests for getting fields from a model or method"""

    field_source = None

    def test_get_fields_overrides_include(self, field_overrides):
        expected_fields_include = [
            {
                "name": "field1",
                "label": "Custom Field 1",
                "type": "str",
                "default": "custom_default",
                "required": True,
            },
            {
                "name": "field2",
                "label": "Field2",
                "type": "int",
                "default": None,
                "required": True,
            },
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["field1", "field2"],
                field_options=field_overrides,
            )
            == expected_fields_include
        )

    def test_get_fields_literal(self, field_overrides):
        expected = [
            {
                "name": "literal",
                "label": "Literal",
                "type": "str",
                "input_type": "select",
                "default": "bar",
                "required": False,
                "choices": [
                    {"value": "foo", "label": "Foo"},
                    {"value": "bar", "label": "Bar"},
                ],
            },
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["literal"],
            )
            == expected
        )

    def test_get_fields_optional(self, field_overrides):
        expected = [
            {
                "name": "optional",
                "label": "Optional",
                "default": None,
                "type": "str",
                "required": False,
            },
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["optional"],
            )
            == expected
        )

    def test_get_fields_overrides_exclude(self, field_overrides):
        expected_fields_exclude = [
            {
                "name": "field2",
                "label": "Field2",
                "type": "int",
                "default": None,
                "required": True,
            },
            {
                "name": "field3",
                "label": "Field3",
                "type": "boolean",
                "default": False,
                "required": False,
            },
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["field1", "field2", "field3"],
                exclude=["field1"],
                field_options=field_overrides,
            )
            == expected_fields_exclude
        )

    def test_get_enum_choices(self, field_overrides):
        expected = [
            {
                "name": "choices_enum",
                "label": "Choices_enum",
                "default": None,
                "type": "str",
                "input_type": "select",
                "required": True,
                "choices": [
                    {"label": "CPP", "value": "cpp"},
                    {"label": "GO", "value": "go"},
                ],
            },
        ]

        fields = NodeTypeField.get_fields(
            self.field_source,
            include=["choices_enum"],
        )
        assert fields == expected


class TestGetFieldsFromModel(GetFieldsBase):
    field_source = TestModel

    def test_exclude_non_allowed_type(self, field_overrides):
        # Extend TestModel with a field of non-allowed type
        class TestModel2(BaseModel):
            field1: str
            field2: int
            field3: bool = False
            field4: TestModel  # non-allowed type

        expected_fields = [
            {
                "name": "field1",
                "label": "Field1",
                "type": "str",
                "default": None,
                "required": True,
            },
            {
                "name": "field2",
                "label": "Field2",
                "type": "int",
                "default": None,
                "required": True,
            },
        ]

        assert (
            NodeTypeField.get_fields(TestModel2, include=["field1", "field2", "field4"])
            == expected_fields
        )


class TestGetFieldsFromMethod(GetFieldsBase):
    field_source = TestModel.loader


class TestGetFieldsFromABC(GetFieldsBase):
    field_source = TestABC
