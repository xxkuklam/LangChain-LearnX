"""A minimal MCP server with ONE read-only tool: list the clients of a local Keycloak.

Run standalone (stdio transport, started by an MCP client):
    uv run python notebooks/keycloak_mcp_server.py
Inspect it interactively:
    uv run mcp dev notebooks/keycloak_mcp_server.py
"""

import os

import httpx
from dotenv import find_dotenv, load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv(find_dotenv(usecwd=True))

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "master")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "mcp-demo")
KEYCLOAK_CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "")

mcp = FastMCP("keycloak")


@mcp.tool()
def list_clients(realm: str = KEYCLOAK_REALM) -> list[dict]:
    """List the clients registered in a Keycloak realm (read-only).

    Args:
        realm: Name of the Keycloak realm. Defaults to the configured realm.
    """
    # 1. Get an access token for the service account of our client (client credentials grant)
    token_response = httpx.post(
        f"{KEYCLOAK_URL}/realms/{realm}/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        },
    )
    if token_response.is_error:
        raise RuntimeError(f"Keycloak token request failed: {token_response.text}")
    token = token_response.json()["access_token"]

    # 2. Call the Admin REST API
    clients_response = httpx.get(
        f"{KEYCLOAK_URL}/admin/realms/{realm}/clients",
        headers={"Authorization": f"Bearer {token}"},
    )
    clients_response.raise_for_status()

    # 3. Return only the useful fields (never secrets)
    return [
        {
            "clientId": c["clientId"],
            "name": c.get("name"),
            "enabled": c["enabled"],
            "protocol": c.get("protocol"),
            "publicClient": c.get("publicClient"),
        }
        for c in clients_response.json()
    ]


if __name__ == "__main__":
    mcp.run()  # stdio transport by default
