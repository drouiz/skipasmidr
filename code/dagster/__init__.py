"""Example Dagster assets."""
from dagster import asset


@asset
def example_asset():
    """An example Dagster asset."""
    return "Hello from Dagster!"
