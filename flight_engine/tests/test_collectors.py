import pytest
from datetime import datetime
from unittest.mock import patch, AsyncMock
from infrastructure.collectors.azul_collector import AzulCollector
from infrastructure.collectors.latam_collector import LatamCollector
from infrastructure.collectors.gol_collector import GolCollector
from infrastructure.collectors.copa_collector import CopaCollector
from infrastructure.collectors.avianca_collector import AviancaCollector
from infrastructure.collectors.tap_collector import TapCollector
from infrastructure.collectors.google_flights_collector import GoogleFlightsCollector
from infrastructure.collectors.kayak_collector import KayakCollector


@pytest.mark.asyncio
async def test_mock_collectors_fetch():
    dep_date = datetime(2026, 6, 22, 10, 0)

    # Azul
    azul = AzulCollector()
    res = await azul.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "AZUL"

    # Latam
    latam = LatamCollector()
    res = await latam.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "LATAM"

    # Gol
    gol = GolCollector()
    res = await gol.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "GOL"

    # Copa
    copa = CopaCollector()
    res = await copa.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "COPA"

    # Avianca
    avianca = AviancaCollector()
    res = await avianca.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "AVIANCA"

    # Tap
    tap = TapCollector()
    res = await tap.fetch_flights("GRU", "FOR", dep_date, 1)
    assert len(res) > 0
    assert res[0].airline == "TAP"


@pytest.mark.asyncio
async def test_real_collectors_mocked():
    dep_date = datetime(2026, 6, 22, 10, 0)

    # Mocking Playwright in Google Flights
    with patch("infrastructure.collectors.google_flights_collector.async_playwright") as mock_pw:
        gf = GoogleFlightsCollector()

        # Setup mock browser / page call chain
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_pw.return_value.__aenter__.return_value.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.query_selector_all = AsyncMock(return_value=[])

        res = await gf.fetch_flights("GRU", "FOR", dep_date, 1)
        assert res == []

    # Mocking Playwright in Kayak
    with patch("infrastructure.collectors.kayak_collector.async_playwright") as mock_pw:
        kayak = KayakCollector()

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_pw.return_value.__aenter__.return_value.chromium.launch = AsyncMock(return_value=mock_browser)
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_page.goto = AsyncMock()
        mock_page.wait_for_timeout = AsyncMock()
        mock_page.evaluate = AsyncMock(return_value="R$ 500\n1h 30m\nDireto\nLATAM\nGRU-FOR")

        res = await kayak.fetch_flights("GRU", "FOR", dep_date, 1)
        assert isinstance(res, list)
