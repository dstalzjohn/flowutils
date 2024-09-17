"""module for url methods"""

import urllib.parse

import pyperclip
import rich
import typer

app = typer.Typer()


@app.command()
def forklift_link(filepath: str):
    """forklift_link"""
    link = create_openforklift_uri(filepath)
    rich.print(f"Your link: [blue]{link}")
    pyperclip.copy(link)
    rich.print("The link was copied to clipboard")


def create_openforklift_uri(filepath: str) -> str:
    """create openforklift uri based on the filepath"""
    return f"openforklift://{escape_url(filepath)}"


def escape_url(url: str) -> str:
    """
    Escapes special characters in a URL string.

    This function takes a URL string and escapes special characters that may cause issues
    when used in certain contexts, such as in Todoist tasks. It specifically handles:
    - Spaces (replaced with %20)
    - Tildes (replaced with %7E)
    - Other special characters that urllib.parse.quote handles by default

    Args:
    url (str): The URL string to be escaped.

    Returns:
    str: The escaped URL string.

    Example:
    >>> escape_url("/path/with spaces/and~tilde.pdf")
    '/path/with%20spaces/and%7Etilde.pdf'
    """
    url = urllib.parse.quote(url, safe="/")
    return url.replace("~", "%7E")
