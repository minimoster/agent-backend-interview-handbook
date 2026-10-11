"""One actual local stdio interoperability run, explicitly on the legacy era."""
import asyncio
import json
import sys
from datetime import timedelta
from importlib.metadata import version
from pathlib import Path
import anyio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS


async def main():
    assert version("mcp") == "1.29.0", "this experiment is version-pinned"
    assert "2026-07-28" not in SUPPORTED_PROTOCOL_VERSIONS
    checks = []
    logs = []
    progress = []

    async def on_log(params):
        logs.append(params.data)

    async def on_progress(value, total, message):
        progress.append((value, total, message))

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).with_name("mcp_legacy_server.py"))],
        env={"PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1"},
    )
    with anyio.fail_after(20):
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream,
                                     read_timeout_seconds=timedelta(seconds=5),
                                     logging_callback=on_log) as session:
                initialized = await session.initialize()
                assert initialized.protocolVersion == "2025-11-25"
                checks.append("legacy_initialize_negotiates_2025_11_25")
                listed = await session.list_tools()
                tools = {tool.name: tool for tool in listed.tools}
                assert set(tools) == {"add", "staged_sum"}
                assert tools["add"].inputSchema["required"] == ["a", "b"]
                assert tools["add"].outputSchema is not None
                checks.append("tools_list_and_input_output_schema")
                result = await session.call_tool("add", {"a": 2, "b": 3})
                assert not result.isError and result.structuredContent["total"] == 5
                checks.append("structured_tool_result")
                invalid = await session.call_tool("add", {"a": 1001, "b": 3})
                assert invalid.isError
                checks.append("out_of_range_rejected")
                missing = await session.call_tool("add", {"a": 2})
                assert missing.isError
                checks.append("missing_argument_rejected")
                coerced = await session.call_tool("add", {"a": "2", "b": 3})
                assert coerced.isError
                checks.append("string_not_coerced_into_strict_integer")
                unknown = await session.call_tool("missing_fixture_tool", {})
                assert unknown.isError
                checks.append("unknown_tool_rejected")
                resources = await session.list_resource_templates()
                assert str(resources.resourceTemplates[0].uriTemplate) == "fixture://greeting/{name}"
                value = await session.read_resource("fixture://greeting/Ada")
                assert "fixture data" in value.contents[0].text
                checks.append("resource_template_list_and_read")
                prompts = await session.list_prompts()
                assert prompts.prompts[0].name == "explain_sum"
                prompt = await session.get_prompt("explain_sum", {"a": "2", "b": "3"})
                assert "fixture integers 2 and 3" in prompt.messages[0].content.text
                checks.append("prompt_list_and_get")
                staged = await session.call_tool("staged_sum", {"values": [1, 2, 3]}, progress_callback=on_progress)
                assert staged.structuredContent["total"] == 6
                assert [p[0] for p in progress] == [1, 2, 3]
                assert all(p[1] == 3 for p in progress)
                assert any("fixture sum started" in str(log) for log in logs)
                checks.append("request_linked_monotonic_progress_and_log")
                failed = await session.call_tool("staged_sum", {"values": []})
                assert failed.isError
                checks.append("tool_business_error_is_not_success")
    print(json.dumps({"python": sys.version.split()[0], "mcp": version("mcp"),
                      "supported_protocols": SUPPORTED_PROTOCOL_VERSIONS,
                      "negotiated_protocol": "2025-11-25", "transport": "stdio",
                      "checks_passed": checks, "check_count": len(checks),
                      "modern_interoperability": "not_tested",
                      "http_auth_cancel_persistence_concurrency": "not_tested"}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
