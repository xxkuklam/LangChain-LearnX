"""A minimal MCP server with two read-only tools for a local Keycloak:
list the realms and list the clients of a realm (with their 'Access settings').

Run standalone (stdio transport, started by an MCP client):
    uv run python notebooks/keycloak_mcp_server.py
Inspect it interactively:
    uv run fastmcp dev inspector notebooks/keycloak_mcp_server.py
"""

import os

import httpx
from dotenv import find_dotenv, load_dotenv
from fastmcp import FastMCP

load_dotenv(find_dotenv(usecwd=True))

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")  # realm where our service client lives
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "mcp-demo")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

mcp = FastMCP("keycloak")


def get_token() -> str:
    """Access token of the service account (client credentials grant)."""
    response = httpx.post(
        f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        },
    )
    if response.is_error:
        raise RuntimeError(f"Keycloak token request failed: {response.text}")
    return response.json()["access_token"]


@mcp.tool()
def list_realms() -> list[str]:
    """List the names of all Keycloak realms (read-only)."""
    response = httpx.get(
        f"{KEYCLOAK_URL}/admin/realms",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    response.raise_for_status()
    return [r["realm"] for r in response.json()]


@mcp.tool()
def list_clients(realm: str) -> list[dict]:
    """List the clients of a Keycloak realm with their 'Access settings' (read-only).

    Args:
        realm: Name of the Keycloak realm (use list_realms to see the available ones).
    """
    response = httpx.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
        headers={"Authorization": f"Bearer {get_token()}"},
    )
    response.raise_for_status()

    # Return the general info + everything from the 'Access settings' section (never secrets)
    return [
        {
            "clientId": c["clientId"],
            "name": c.get("name"),
            "enabled": c["enabled"],
            "protocol": c.get("protocol"),
            "publicClient": c.get("publicClient"),
            "rootUrl": c.get("rootUrl"),
            "baseUrl": c.get("baseUrl"),  # Home URL
            "redirectUris": c.get("redirectUris"),  # Valid redirect URIs
            "postLogoutRedirectUris": c.get("attributes", {}).get("post.logout.redirect.uris"),
            "webOrigins": c.get("webOrigins"),
            "adminUrl": c.get("adminUrl"),  # Admin URL
        }
        for c in response.json()
    ]


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
