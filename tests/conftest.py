"""
tests/conftest.py
Shared test fixtures for the Horizon Exoplanet Platform.
"""
import pytest
import numpy as np
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.core.config import settings


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def async_client():
    """Async HTTP test client with SQLite backend."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client


@pytest.fixture
def synthetic_light_curve():
    """Generate a synthetic TESS-like light curve with one transit."""
    rng = np.random.default_rng(42)
    time = np.linspace(0, 27, 10000)
    flux = np.ones(len(time))

    # Inject transit at P=3.5 d, depth=0.01, duration=0.1 d
    period = 3.5
    epoch = 2.0
    duration = 0.1
    depth = 0.01
    for k in range(int(27 / period) + 1):
        tc = epoch + k * period
        mask = np.abs(time - tc) < duration / 2
        flux[mask] = 1.0 - depth

    flux += rng.normal(0, 0.001, len(time))
    return time, flux, np.ones(len(time)) * 0.001
