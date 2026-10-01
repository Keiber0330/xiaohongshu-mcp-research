package main

// MCP discovery harness for xpzouying/xiaohongshu-mcp.
// Copy into the repo root and run:  go test -run TestMCPDiscovery -v .
// Mounts the project's real gin router (incl. /mcp Streamable HTTP handler)
// in-process. Does NOT start the browser, so no Xiaohongshu traffic happens;
// only tools that don't need a browser page can return real results.

import (
	"context"
	"encoding/json"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/modelcontextprotocol/go-sdk/mcp"
)

func TestMCPDiscovery(t *testing.T) {
	app := NewAppServer(NewXiaohongshuService(), "")
	srv := httptest.NewServer(setupRoutes(app))
	defer srv.Close()

	ctx := context.Background()
	client := mcp.NewClient(&mcp.Implementation{Name: "discovery-harness", Version: "0.1"}, nil)
	sess, err := client.Connect(ctx, &mcp.StreamableClientTransport{Endpoint: srv.URL + "/mcp"}, nil)
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer sess.Close()

	init := sess.InitializeResult()
	t.Logf("server: %s %s, protocol %s", init.ServerInfo.Name, init.ServerInfo.Version, init.ProtocolVersion)

	res, err := sess.ListTools(ctx, nil)
	if err != nil {
		t.Fatalf("tools/list: %v", err)
	}
	t.Logf("tools/list returned %d tools", len(res.Tools))
	out, _ := json.MarshalIndent(res.Tools, "", "  ")
	if p := os.Getenv("TOOLS_OUT"); p != "" {
		_ = os.WriteFile(p, out, 0o644)
	}
	for _, tl := range res.Tools {
		ro := tl.Annotations != nil && tl.Annotations.ReadOnlyHint
		t.Logf("  %-24s readOnly=%v  %s", tl.Name, ro, tl.Description)
	}

	// One real tools/call. Without the bundled browser (or network) this shows
	// the failure path a Claude client would see.
	call, err := sess.CallTool(ctx, &mcp.CallToolParams{Name: "search_feeds", Arguments: map[string]any{"keyword": "咖啡"}})
	if err != nil {
		t.Fatalf("tools/call transport error: %v", err)
	}
	for _, c := range call.Content {
		if tc, ok := c.(*mcp.TextContent); ok {
			t.Logf("search_feeds isError=%v text=%.300s", call.IsError, tc.Text)
		}
	}
}
