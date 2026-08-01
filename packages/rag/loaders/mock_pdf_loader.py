"""
Mock PDF Document Loader Implementation.

Simulates loading PDF documents (e.g. Annual Reports, SEBI Filings, Research Notes).
No external PDF library or downloading required.
"""

from packages.rag.loaders.base import BaseDocumentLoader
from packages.rag.models.document import Document, DocumentMetadata


class MockPDFLoader(BaseDocumentLoader):
    """
    Mock PDF Document Loader for development and unit tests.
    """

    def load(self, source: str) -> list[Document]:
        """
        Construct a deterministic mock Document representation for a given PDF source path.
        """
        title = source.split("/")[-1].replace(".pdf", "").title()
        sample_text = (
            f"MANAGEMENT DISCUSSION AND ANALYSIS REPORT FOR {title.upper()}.\n"
            "The Company achieved strong financial growth during the financial year. "
            "Revenue from operations increased by 18.5% YoY, driven by solid demand across all business segments. "
            "Return on Capital Employed (ROCE) expanded by 240 bps to 22.4%. "
            "The balance sheet remains robust with minimal debt and conservative leverage ratios."
        )

        metadata = DocumentMetadata(
            source=source,
            title=f"{title} Annual Report",
            author="HedgeFundAI Research",
            custom_metadata={"file_type": "PDF", "mock": True},
        )

        return [Document(content=sample_text, metadata=metadata)]
