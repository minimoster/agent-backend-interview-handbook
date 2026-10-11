"""Original local-only server. SDK mcp==1.29.0; legacy protocol 2025-11-25.
No network access, credentials, user files, or production authorization claims.
"""
from typing import Annotated
from mcp.server.fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

mcp = FastMCP("contract-fixture")
BoundedInt = Annotated[int, Field(strict=True, ge=-1000, le=1000)]


class SumResult(BaseModel):
    total: int
    fixture: bool = True


@mcp.tool()
def add(a: BoundedInt, b: BoundedInt) -> SumResult:
    """Add two bounded fixture integers; no external side effects."""
    return SumResult(total=a + b)


@mcp.tool()
async def staged_sum(values: list[BoundedInt], ctx: Context) -> SumResult:
    """Sum at most four fixture values and emit request-linked progress."""
    if not 1 <= len(values) <= 4:
        raise ValueError("values must contain 1 to 4 integers")
    await ctx.info("fixture sum started")
    result = 0
    for index, value in enumerate(values, 1):
        result += value
        await ctx.report_progress(index, len(values), "fixture step")
    return SumResult(total=result)


@mcp.resource("fixture://greeting/{name}")
def greeting(name: str) -> str:
    """Return a fictional greeting, not private file contents."""
    if name not in {"Ada", "Lin"}:
        raise ValueError("unknown fixture name")
    return f"Hello, {name}. This is fixture data."


@mcp.prompt()
def explain_sum(a: int, b: int) -> str:
    """Provide a bounded teaching prompt, not an execution permission."""
    return f"Explain how to add the fixture integers {a} and {b}."


if __name__ == "__main__":
    mcp.run(transport="stdio")
