import requests
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import PromptMessage, TextContent
from typing import List

# Initialize MCP server
mcp = FastMCP("TwitterUsernameChanges", dependencies=["mcp[cli]", "requests"])

# Tool: Query username change history for a Twitter user
@mcp.tool()
def query_username_changes(screen_name: str, ctx: Context) -> str:
    """
    Query the username change history for a Twitter user using the memory.lol API.

    Parameters:
        screen_name (str): The current Twitter screen name (handle) of the user, without the '@' symbol.
                          For example, use 'OSINT_Ukraine' for '@OSINT_Ukraine'.
                          Case-insensitive and must be a valid Twitter handle.

    Returns:
        A formatted string containing the username change history, including user ID and timestamps.
        If no history is found or an error occurs, returns an error message.
    """
    ctx.info(f"Querying username changes for screen name: {screen_name}")
    
    # Fetch data from memory.lol API
    try:
        response = requests.get(f"https://api.memory.lol/v1/tw/{screen_name}")
        response.raise_for_status()
        data = response.json()
    except requests.HTTPError as e:
        return f"Error: Failed to fetch data for {screen_name} (status {e.response.status_code})"
    except requests.RequestException:
        return f"Error: Network issue while fetching data for {screen_name}"

    if not data.get("accounts"):
        return f"No username change history found for {screen_name}"

    # Format username change history
    formatted_history = []
    for account in data["accounts"]:
        user_id = account["id_str"]
        screen_names = account["screen_names"]
        history = "\n".join(
            f"- {name} ({' to '.join(dates) if isinstance(dates, list) else dates})"
            for name, dates in screen_names.items()
        )
        formatted_history.append(f"User ID {user_id}:\n{history}")
    
    return f"Username change history for {screen_name}:\n\n" + "\n\n".join(formatted_history)

# Prompt: Provide a template for querying username changes
@mcp.prompt()
def username_change_prompt(screen_name: str) -> List[PromptMessage]:
    """Prompt template for querying Twitter username changes."""
    return [
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text=f"Please show the username change history for Twitter user @{screen_name}"
            )
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(
                type="text",
                text=f"I'll fetch the username change history for @{screen_name}."
            )
        )
    ]

# Run the server
if __name__ == "__main__":
    mcp.run()