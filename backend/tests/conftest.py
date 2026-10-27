import pytest

from app.data.repository import get_repository
from tests.fixtures.sample_data import get_sample_actuals_df, get_sample_forecasts_df


@pytest.fixture
def sample_repo():
    repo = get_repository()
    repo._actuals = get_sample_actuals_df()
    repo._forecasts = get_sample_forecasts_df()
    repo._loaded = True
    yield repo
    repo._loaded = False
    repo._actuals = None
    repo._forecasts = None
