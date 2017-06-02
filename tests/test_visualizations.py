import os
import pytest

from carto.visualizations import VisualizationManager


@pytest.fixture(scope="module")
def visualization_manager(api_key_auth_client):
    """
    Returns a visualization manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid \
                                APIKeyAuthClient object
    :return: DataManager instance
    """
    return VisualizationManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_visualizations(visualization_manager, user):
    """
    Get all the visualizations from the API
    :param visualization_manager: Fixture that provides a user manager to \
                                    work with
    :param user: If valid, we'll check the number of returned visualizations \
                    exactly against the expected value
    """
    visualizations = visualization_manager.all()

    # If are testing against an enterprise account and have a valid user,
    # we can easily know how many visualizations to expect
    if user is not None:
        assert len(visualizations) == user.all_visualization_count
    else:
        assert len(visualizations) >= 0
