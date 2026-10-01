"""Generic MCP probe: connect to a Streamable-HTTP MCP server, list tools,
optionally call one tool, and dump everything to JSON.

usage: python mcp_probe.py <mcp_url> <out.json> [tool_name '<json args>']
"""
import asyncio, json, sys, time
from fastmcp import Client


async def main():
    url, out = sys.argv[1], sys.argv[2]
    report = {"url": url, "probed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    # mode="legacy" forces the classic initialize handshake that Claude Desktop /
    # Claude Code clients perform, so the probe exercises the same path they use.
    try:
        client = Client(url, mode="legacy")
    except TypeError:  # older fastmcp without the mode switch
        client = Client(url)
    async with client as c:
        init = c.initialize_result
        report["server"] = {"name": init.serverInfo.name, "version": init.serverInfo.version,
                            "protocol": init.protocolVersion}
        tools = await c.list_tools()
        report["tools"] = [t.model_dump(exclude_none=True) for t in tools]
        print(f"server={init.serverInfo.name} {init.serverInfo.version} tools={len(tools)}")
        for t in tools:
            print(f"  - {t.name}: params={list((t.inputSchema or {}).get('properties', {}))}")
        if len(sys.argv) > 4:
            name, args = sys.argv[3], json.loads(sys.argv[4])
            t0 = time.time()
            res = await c.call_tool(name, args, raise_on_error=False)
            report["call"] = {"tool": name, "args": args, "seconds": round(time.time() - t0, 2),
                              "is_error": res.is_error,
                              "content": [x.model_dump(exclude_none=True) for x in res.content],
                              "structured": res.structured_content}
            print(f"call {name} -> is_error={res.is_error} in {report['call']['seconds']}s")
            print(json.dumps(report["call"]["structured"] or report["call"]["content"], ensure_ascii=False)[:800])
    with open(out, "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


asyncio.run(main())
