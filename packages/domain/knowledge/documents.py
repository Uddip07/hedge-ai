"""
Research Document Domain Entities and Models for the Indian AI Hedge Fund Platform.

Provides ResearchDocument base entity along with specialized document types:
AnnualReport, NewsArticle, SEBICircular, RBIReport, BudgetDocument, Transcript,
ResearchNote, and PDFDocument. Pure domain models.
"""

from dataclasses import dataclass, field
from typing import Any

from packages.domain.enums.research import DocumentType
from packages.domain.exceptions import ValidationError
from packages.domain.value_objects.core.price import Price
from packages.domain.value_objects.identifiers.ticker import Ticker
from packages.domain.value_objects.identifiers.uuid_wrappers import DocumentId
from packages.domain.value_objects.metrics.scores import ConfidenceScore
from packages.domain.value_objects.temporal.financial_periods import FiscalYear
from packages.domain.value_objects.temporal.timestamps import Timestamp


@dataclass
class ResearchDocument:
    """
    ResearchDocument Base Entity.

    Attributes:
        id (DocumentId): Unique document identifier.
        title (str): Document title / headline.
        doc_type (DocumentType): Document classification (ANNUAL_REPORT, SEBI_CIRCULAR, etc.).
        content (str): Textual body content.
        author (Optional[str]): Document author or publishing institution.
        ticker (Optional[Ticker]): Associated asset ticker symbol if applicable.
        source_url (Optional[str]): Originating URL reference.
        published_at (Timestamp): Publication timestamp (UTC).
        created_at (Timestamp): Ingestion timestamp (UTC).
        metadata (Dict[str, Any]): Additional document metadata attributes.
    """

    title: str
    content: str
    published_at: Timestamp
    doc_type: DocumentType = DocumentType.RESEARCH_NOTE
    id: DocumentId = field(default_factory=DocumentId.generate)
    author: str | None = None
    ticker: Ticker | None = None
    source_url: str | None = None
    created_at: Timestamp = field(default_factory=Timestamp.now_utc)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.id, DocumentId):
            object.__setattr__(self, "id", DocumentId(self.id))
        if not isinstance(self.doc_type, DocumentType):
            object.__setattr__(self, "doc_type", DocumentType(self.doc_type))
        if self.ticker is not None and not isinstance(self.ticker, Ticker):
            object.__setattr__(self, "ticker", Ticker(self.ticker))
        if not isinstance(self.published_at, Timestamp):
            object.__setattr__(self, "published_at", Timestamp(self.published_at))
        if not isinstance(self.created_at, Timestamp):
            object.__setattr__(self, "created_at", Timestamp(self.created_at))

        if not self.title.strip():
            raise ValidationError("ResearchDocument title cannot be empty.")
        if not self.content.strip():
            raise ValidationError("ResearchDocument content cannot be empty.")

    @property
    def word_count(self) -> int:
        """Return total word count of content payload."""
        return len(self.content.split())

    def is_regulatory(self) -> bool:
        """Return True if document originates from an official regulator (SEBI, RBI)."""
        return self.doc_type.is_regulatory()

    def to_dict(self) -> dict[str, Any]:
        """Serialize ResearchDocument to dictionary."""
        return {
            "id": self.id.to_dict(),
            "title": self.title,
            "doc_type": self.doc_type.value,
            "content": self.content,
            "word_count": self.word_count,
            "author": self.author,
            "ticker": self.ticker.to_dict() if self.ticker else None,
            "source_url": self.source_url,
            "published_at": self.published_at.to_dict(),
            "created_at": self.created_at.to_dict(),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchDocument":
        """Deserialize dictionary to ResearchDocument."""
        ticker_obj = Ticker.from_dict(data["ticker"]) if data.get("ticker") else None

        return cls(
            id=DocumentId.from_dict(data["id"]),
            title=data["title"],
            doc_type=DocumentType(data["doc_type"]),
            content=data["content"],
            author=data.get("author"),
            ticker=ticker_obj,
            source_url=data.get("source_url"),
            published_at=Timestamp.from_dict(data["published_at"]),
            created_at=Timestamp.from_dict(data["created_at"]),
            metadata=dict(data.get("metadata", {})),
        )

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ResearchDocument):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class AnnualReport(ResearchDocument):
    """
    AnnualReport Entity specializing ResearchDocument for corporate annual filings.
    """

    fiscal_year: FiscalYear | None = None
    auditor_name: str | None = None
    has_qualified_opinion: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.ANNUAL_REPORT)
        super().__post_init__()


@dataclass
class NewsArticle(ResearchDocument):
    """
    NewsArticle Entity specializing ResearchDocument for financial news.
    """

    publisher: str = "Unknown"
    sentiment_score: ConfidenceScore | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.NEWS_ARTICLE)
        super().__post_init__()


@dataclass
class SEBICircular(ResearchDocument):
    """
    SEBICircular Entity specializing ResearchDocument for Indian SEBI regulatory updates.
    """

    circular_number: str = ""
    category: str = "Regulatory"
    is_mandatory: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.SEBI_CIRCULAR)
        super().__post_init__()


@dataclass
class RBIReport(ResearchDocument):
    """
    RBIReport Entity specializing ResearchDocument for Reserve Bank of India policy reports.
    """

    policy_type: str = "Monetary Policy"
    rate_change_bps: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.RBI_REPORT)
        super().__post_init__()


@dataclass
class BudgetDocument(ResearchDocument):
    """
    BudgetDocument Entity specializing ResearchDocument for Union / State budget announcements.
    """

    fiscal_year: FiscalYear | None = None
    ministry: str = "Ministry of Finance"

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.BUDGET_DOCUMENT)
        super().__post_init__()


@dataclass
class Transcript(ResearchDocument):
    """
    Transcript Entity specializing ResearchDocument for corporate earnings calls.
    """

    event_type: str = "EARNINGS_CALL"
    quarter: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.TRANSCRIPT)
        super().__post_init__()


@dataclass
class ResearchNote(ResearchDocument):
    """
    ResearchNote Entity specializing ResearchDocument for internal or broker research notes.
    """

    analyst_name: str = "Internal AGY Analyst"
    target_price: Price | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "doc_type", DocumentType.RESEARCH_NOTE)
        super().__post_init__()


@dataclass
class PDFDocument(ResearchDocument):
    """
    PDFDocument Entity specializing ResearchDocument for binary PDF document ingestion.
    """

    file_path: str = ""
    page_count: int = 1
    file_hash: str = ""

    def __post_init__(self) -> None:
        super().__post_init__()
