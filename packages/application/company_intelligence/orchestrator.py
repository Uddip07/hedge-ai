"""
Company Intelligence Orchestrator.

Main entrypoint for executing end-to-end Company Intelligence research analysis workflows.
Instantiates required infrastructure services, coordinates pipeline steps, calls ResearchReportBuilder,
and returns the final ResearchReport aggregate.
"""

from packages.application.company_intelligence.exceptions import CompanyIntelligenceError
from packages.application.company_intelligence.models import ResearchReport
from packages.application.company_intelligence.pipeline import CompanyIntelligencePipeline
from packages.application.company_intelligence.report_builder import ResearchReportBuilder
from packages.application.company_intelligence.services import (
    CompanyAgentCoordinatorService,
    CompanyDataRetrievalService,
    CompanyDocumentService,
)
from packages.application.company_intelligence.workflow import CompanyIntelligenceWorkflow
from packages.infrastructure.market_data.providers.yahoo_provider import (
    YahooMarketDataProvider,
)
from packages.infrastructure.market_data.registries.quote_registry import (
    CorporateActionProviderRegistry,
    ETFProviderRegistry,
    FundamentalProviderRegistry,
    MacroProviderRegistry,
    NewsProviderRegistry,
    QuoteProviderRegistry,
)
from packages.infrastructure.market_data.services.company_profile_service import (
    CompanyProfileService,
)
from packages.infrastructure.market_data.services.corporate_service import (
    CorporateActionService,
)
from packages.infrastructure.market_data.services.economic_calendar_service import (
    EconomicCalendarService,
)
from packages.infrastructure.market_data.services.exchange_service import (
    ExchangeService,
)
from packages.infrastructure.market_data.services.fundamental_service import (
    FundamentalService,
)
from packages.infrastructure.market_data.services.historical_service import (
    HistoricalService,
)
from packages.infrastructure.market_data.services.macro_service import MacroService
from packages.infrastructure.market_data.services.news_service import NewsService
from packages.infrastructure.market_data.services.quote_service import QuoteService


class CompanyIntelligenceOrchestrator:
    """
    Primary Application Orchestrator for the Company Intelligence Engine.
    """

    def __init__(
        self,
        data_retrieval_service: CompanyDataRetrievalService | None = None,
        document_service: CompanyDocumentService | None = None,
        agent_coordinator_service: CompanyAgentCoordinatorService | None = None,
        report_builder: ResearchReportBuilder | None = None,
    ) -> None:
        if data_retrieval_service is None:
            provider = YahooMarketDataProvider()

            quote_reg = QuoteProviderRegistry()
            quote_reg.register("yahoo", provider)

            fund_reg = FundamentalProviderRegistry()
            fund_reg.register("yahoo", provider)

            news_reg = NewsProviderRegistry()
            news_reg.register("yahoo", provider)

            macro_reg = MacroProviderRegistry()
            macro_reg.register("yahoo", provider)

            corp_reg = CorporateActionProviderRegistry()
            corp_reg.register("yahoo", provider)

            etf_reg = ETFProviderRegistry()
            etf_reg.register("yahoo", provider)

            data_retrieval_service = CompanyDataRetrievalService(
                quote_service=QuoteService(registry=quote_reg, default_provider="yahoo"),
                historical_service=HistoricalService(registry=quote_reg, default_provider="yahoo"),
                fundamental_service=FundamentalService(registry=fund_reg, default_provider="yahoo"),
                company_profile_service=CompanyProfileService(
                    registry=fund_reg, default_provider="yahoo"
                ),
                corporate_service=CorporateActionService(
                    registry=corp_reg, default_provider="yahoo"
                ),
                news_service=NewsService(registry=news_reg, default_provider="yahoo"),
                macro_service=MacroService(registry=macro_reg, default_provider="yahoo"),
                economic_calendar_service=EconomicCalendarService(
                    registry=macro_reg, default_provider="yahoo"
                ),
                exchange_service=ExchangeService(registry=quote_reg, default_provider="yahoo"),
            )

        self.data_retrieval_service = data_retrieval_service
        self.document_service = document_service or CompanyDocumentService()
        self.agent_coordinator_service = (
            agent_coordinator_service or CompanyAgentCoordinatorService()
        )
        self.report_builder = report_builder or ResearchReportBuilder()

        self.pipeline = CompanyIntelligencePipeline(
            data_retrieval_service=self.data_retrieval_service,
            document_service=self.document_service,
            agent_coordinator_service=self.agent_coordinator_service,
        )
        self.workflow = CompanyIntelligenceWorkflow(pipeline=self.pipeline)

    def analyze_company(self, ticker_symbol: str, session_id: str | None = None) -> ResearchReport:
        """
        Execute complete Company Intelligence research analysis for a ticker.

        Args:
            ticker_symbol (str): Target stock ticker symbol (e.g. 'RELIANCE', 'INFY.NSE').
            session_id (str | None): Optional analysis session ID.

        Returns:
            ResearchReport: Structured institutional research report.
        """
        try:
            workflow_payload = self.workflow.run_workflow(ticker_symbol, session_id=session_id)
            report = self.report_builder.build_report(workflow_payload)
            return report
        except Exception as err:
            raise CompanyIntelligenceError(
                f"Failed to orchestrate company analysis for '{ticker_symbol}': {err}",
                details={"ticker": ticker_symbol},
            ) from err
