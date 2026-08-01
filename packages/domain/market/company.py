"""
Company Entity for the Indian AI Hedge Fund Domain.

Represents a corporate entity listed or operating in Indian financial markets.
Tracks corporate metadata, CIN (Corporate Identity Number), sector classifications,
and associated exchange listings.
"""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Any

from packages.domain.enums.market import ExchangeType, MarketSegment
from packages.domain.exceptions.business import DuplicateEntityError, EntityNotFoundError
from packages.domain.exceptions.validation import ValidationError
from packages.domain.market.listing import Listing


@dataclass
class Company:
    """
    Domain Entity representing a corporate enterprise listed on NSE/BSE.

    Attributes:
        id (uuid.UUID): Unique company identifier.
        name (str): Full legal corporate name (e.g. "Reliance Industries Limited").
        sector (MarketSegment): Sector/Cap classification (e.g. LARGE_CAP, CASH).
        industry (str): Industry description (e.g. "Oil & Gas", "Information Technology").
        cin (str | None): MCA Corporate Identity Number (21-character alphanumeric).
        incorporation_date (date | None): Official company incorporation date.
        listings (list[Listing]): List of exchange listing entities for this company.
        created_at (datetime): Entity creation timestamp (UTC).
        updated_at (datetime): Entity last update timestamp (UTC).
    """

    name: str
    sector: MarketSegment
    industry: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    cin: str | None = None
    incorporation_date: date | None = None
    listings: list[Listing] = field(default_factory=list)
    market_cap: float | None = None
    enterprise_value: float | None = None
    employees: int | None = None
    country: str | None = None
    currency: str | None = None
    website: str | None = None
    long_business_summary: str | None = None
    beta: float | None = None
    trailing_pe: float | None = None
    forward_pe: float | None = None
    book_value: float | None = None
    price_to_book: float | None = None
    dividend_yield: float | None = None
    fifty_two_week_high: float | None = None
    fifty_two_week_low: float | None = None
    average_volume: float | None = None
    shares_outstanding: float | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValidationError("Company name cannot be empty.")
        if not self.industry or not self.industry.strip():
            raise ValidationError("Industry cannot be empty.")
        if self.cin:
            cin_clean = self.cin.strip().upper()
            if len(cin_clean) != 21:
                raise ValidationError(
                    f"Invalid MCA CIN length '{self.cin}'. CIN must be exactly 21 characters."
                )
            self.cin = cin_clean

    def add_listing(self, listing: Listing) -> None:
        """Add an exchange listing entity to this company."""
        for existing in self.listings:
            if existing.exchange == listing.exchange:
                raise DuplicateEntityError(
                    f"Company '{self.name}' already has a listing on exchange '{listing.exchange.value}'."
                )
        self.listings.append(listing)
        self._touch()

    def remove_listing(self, listing_id: uuid.UUID) -> None:
        """
        Remove an exchange listing by ID.

        Raises:
            EntityNotFoundError: If the listing ID is not found.
        """
        initial_len = len(self.listings)
        self.listings = [lst for lst in self.listings if lst.id != listing_id]
        if len(self.listings) == initial_len:
            raise EntityNotFoundError(
                f"Listing '{listing_id}' not found for company '{self.name}'.",
                context={"company_id": str(self.id), "listing_id": str(listing_id)},
            )
        self._touch()

    def get_listing_for_exchange(self, exchange: ExchangeType) -> Listing | None:
        """Return the listing for a specific exchange venue if present."""
        for listing in self.listings:
            if listing.exchange == exchange:
                return listing
        return None

    def get_primary_listing(self) -> Listing | None:
        """Return the primary exchange listing."""
        for listing in self.listings:
            if listing.is_primary:
                return listing
        return self.listings[0] if self.listings else None

    def _touch(self) -> None:
        """Update the updated_at timestamp to now UTC."""
        self.updated_at = datetime.now(UTC)

    def to_dict(self) -> dict[str, Any]:
        """Serialize Company entity to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "sector": self.sector.value,
            "industry": self.industry,
            "cin": self.cin,
            "incorporation_date": (
                self.incorporation_date.isoformat() if self.incorporation_date else None
            ),
            "listings": [lst.to_dict() for lst in self.listings],
            "market_cap": self.market_cap,
            "enterprise_value": self.enterprise_value,
            "employees": self.employees,
            "country": self.country,
            "currency": self.currency,
            "website": self.website,
            "long_business_summary": self.long_business_summary,
            "beta": self.beta,
            "trailing_pe": self.trailing_pe,
            "forward_pe": self.forward_pe,
            "book_value": self.book_value,
            "price_to_book": self.price_to_book,
            "dividend_yield": self.dividend_yield,
            "fifty_two_week_high": self.fifty_two_week_high,
            "fifty_two_week_low": self.fifty_two_week_low,
            "average_volume": self.average_volume,
            "shares_outstanding": self.shares_outstanding,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Company":
        """Deserialize dictionary to Company entity."""
        inc_date = (
            date.fromisoformat(data["incorporation_date"])
            if data.get("incorporation_date")
            else None
        )
        listings = [Listing.from_dict(lst) for lst in data.get("listings", [])]
        return cls(
            id=uuid.UUID(data["id"]),
            name=data["name"],
            sector=MarketSegment(data["sector"]),
            industry=data["industry"],
            cin=data.get("cin"),
            incorporation_date=inc_date,
            listings=listings,
            market_cap=data.get("market_cap"),
            enterprise_value=data.get("enterprise_value"),
            employees=data.get("employees"),
            country=data.get("country"),
            currency=data.get("currency"),
            website=data.get("website"),
            long_business_summary=data.get("long_business_summary"),
            beta=data.get("beta"),
            trailing_pe=data.get("trailing_pe"),
            forward_pe=data.get("forward_pe"),
            book_value=data.get("book_value"),
            price_to_book=data.get("price_to_book"),
            dividend_yield=data.get("dividend_yield"),
            fifty_two_week_high=data.get("fifty_two_week_high"),
            fifty_two_week_low=data.get("fifty_two_week_low"),
            average_volume=data.get("average_volume"),
            shares_outstanding=data.get("shares_outstanding"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )
