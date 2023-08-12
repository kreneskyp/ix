from typing import List, TypeVar, Generic

from pydantic import BaseModel
from django.core.paginator import Paginator
from django.db.models import QuerySet
from graphene import Int, ObjectType, Boolean


class GenericPage(ObjectType):
    """
    Represents a paginated result set with metadata.

    TODO: to be deprecated in favor of pydantic QueryPage.

    Attributes:
        page_number (int): The current page number.
        pages (int): The total number of pages.
        count (int): The total count of items across all pages.
        has_next (bool): Indicates if there is a next page.
        has_previous (bool): Indicates if there is a previous page.
    """

    page_number = Int()
    pages = Int()
    count = Int()
    has_next = Boolean()
    has_previous = Boolean()

    @classmethod
    def paginate(
        cls, queryset: QuerySet, limit: int = 10, offset: int = 0
    ) -> "GenericPage":
        """
        Paginates a queryset and returns a GenericPage instance.

        Args:
            queryset (QuerySet): The original queryset to paginate.
            limit (int): The maximum number of items per page.
            offset (int): The starting index of the current page.

        Returns:
            GenericPage: The paginated result set with metadata.
        """
        paginator = Paginator(queryset, limit if limit is not None else 10)
        page_number = offset // (limit if limit is not None else 10) + 1
        page = paginator.get_page(page_number)
        return cls(
            page_number=page.number,
            pages=page.paginator.num_pages,
            count=page.paginator.count,
            has_next=page.has_next(),
            has_previous=page.has_previous(),
            objects=page.object_list,
        )


T = TypeVar("T")


class QueryPage(BaseModel, Generic[T]):
    """
    Represents a paginated result set with metadata.

    Attributes:
        page_number (int): The current page number.
        pages (int): The total number of pages.
        count (int): The total count of items across all pages.
        has_next (bool): Indicates if there is a next page.
        has_previous (bool): Indicates if there is a previous page.
    """

    page_number: int
    pages: int
    count: int
    has_next: bool
    has_previous: bool
    objects: List[T]

    @classmethod
    def paginate(
        cls,
        output_model: BaseModel,
        queryset: QuerySet,
        limit: int = 10,
        offset: int = 0,
    ) -> "QueryPage":
        """
        Paginates a queryset and returns a GenericPage instance.

        Args:
            queryset (QuerySet): The original queryset to paginate.
            limit (int): The maximum number of items per page.
            offset (int): The starting index of the current page.

        Returns:
            GenericPage: The paginated result set with metadata.
        """
        paginator = Paginator(queryset, limit if limit is not None else 10)
        page_number = offset // (limit if limit is not None else 10) + 1
        page = paginator.get_page(page_number)
        objects = [output_model.from_orm(obj).dict() for obj in page.object_list]

        return cls(
            page_number=page.number,
            pages=page.paginator.num_pages,
            count=page.paginator.count,
            has_next=page.has_next(),
            has_previous=page.has_previous(),
            objects=objects,
        )
