from mcp.server.fastmcp import FastMCP

mcp = FastMCP("prompt-server")

# Prompt: summarize
@mcp.prompt(
    name="summarize",
    description="Summarize the given text in a concise way"
)
async def summarize_prompt():
    return [
        {
            "role": "assistant",
            "content": "You are a helpful assistant that summarizes text clearly and concisely."
        },
        {
            "role": "user",
            "content": "Summarize the following content:"
        }
    ]

@mcp.prompt(
    name="code_review",
    description="Review code with a specific language and focus"
)
async def code_review_prompt(language: str, focus: str):
    return [
        {
            "role": "assistant",
            "content": (
                f"You are an expert {language} developer. "
                f"Review the code with focus on {focus}."
            )
        },
        {
            "role": "user",
            "content": "Please review the following code:"
        }
    ]


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
