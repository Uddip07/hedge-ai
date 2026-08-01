"""
Base Mapper Abstraction for Application Layer.

Provides generic interface contracts for transforming between Domain Entities/Value Objects
and Application Data Transfer Objects (DTOs).
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from packages.application.dto.base import BaseDTO

TDomain = TypeVar("TDomain")
TDTO = TypeVar("TDTO", bound=BaseDTO)


class BaseMapper(ABC, Generic[TDomain, TDTO]):
    """
    Abstract Generic Mapper Contract.

    Decouples domain model structures from external boundary DTO schemas.
    """

    @abstractmethod
    def to_dto(self, domain: TDomain) -> TDTO:
        """Map domain model/entity to application DTO."""

    @abstractmethod
    def to_domain(self, dto: TDTO) -> TDomain:
        """Map application DTO to domain model/entity."""

    def to_dto_list(self, domain_list: list[TDomain]) -> list[TDTO]:
        """Convert list of domain models to list of DTOs."""
        return [self.to_dto(item) for item in domain_list]

    def to_domain_list(self, dto_list: list[TDTO]) -> list[TDomain]:
        """Convert list of DTOs to list of domain models."""
        return [self.to_domain(dto) for dto in dto_list]
