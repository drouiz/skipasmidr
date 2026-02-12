"""Example Prefect flow."""
from prefect import flow, task


@task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"


@flow
def example_flow(name: str = "World"):
    """An example Prefect flow."""
    message = say_hello(name)
    print(message)
    return message


if __name__ == "__main__":
    example_flow()
