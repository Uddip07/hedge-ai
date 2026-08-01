"""
Application DTO Package.

Exports BaseDTO and domain-specific DTO classes.
"""

from packages.application.dto.analyze_stock_dto import AnalyzeStockResultDTO
from packages.application.dto.base import BaseDTO

__all__ = ["BaseDTO", "AnalyzeStockResultDTO"]
