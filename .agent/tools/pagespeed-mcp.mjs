#!/usr/bin/env node

/**
 * PageSpeed Insights MCP Server
 *
 * Shared MCP tool for analyzing web performance using Google PageSpeed Insights API.
 * Used by all AI tools (Claude Code, Gemini, Antigravity, OpenCode) via .mcp.json.
 *
 * Requirements:
 *   - PAGESPEED_API_KEY env var (get free key at https://console.cloud.google.com/apis/credentials)
 *   - Enable "PageSpeed Insights API" at https://console.cloud.google.com/apis/library
 *
 * Usage in .mcp.json:
 *   {
 *     "pagespeed": {
 *       "type": "stdio",
 *       "command": "node",
 *       "args": [".agent/tools/pagespeed-mcp.mjs"],
 *       "env": { "PAGESPEED_API_KEY": "${PAGESPEED_API_KEY}" }
 *     }
 *   }
 */

import { createInterface } from "node:readline";

const API_KEY = process.env.PAGESPEED_API_KEY;

// MCP Protocol: JSON-RPC over stdio
const rl = createInterface({ input: process.stdin });

function sendResponse(id, result) {
  const response = JSON.stringify({ jsonrpc: "2.0", id, result });
  process.stdout.write(`Content-Length: ${Buffer.byteLength(response)}\r\n\r\n${response}`);
}

function sendError(id, code, message) {
  const response = JSON.stringify({
    jsonrpc: "2.0",
    id,
    error: { code, message },
  });
  process.stdout.write(`Content-Length: ${Buffer.byteLength(response)}\r\n\r\n${response}`);
}

async function analyzePageSpeed(url, strategy = "mobile") {
  if (!API_KEY) {
    return "Error: PAGESPEED_API_KEY not configured. Get a free key at https://console.cloud.google.com/apis/credentials and enable the PageSpeed Insights API.";
  }

  const apiUrl =
    `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?` +
    `url=${encodeURIComponent(url)}&strategy=${strategy}&key=${API_KEY}` +
    `&category=PERFORMANCE&category=ACCESSIBILITY&category=BEST_PRACTICES&category=SEO`;

  const res = await fetch(apiUrl);
  if (!res.ok) {
    return `API Error: HTTP ${res.status} ${res.statusText}`;
  }

  const data = await res.json();

  if (data.error) {
    return `API Error: ${data.error.message}`;
  }

  if (!data.lighthouseResult) {
    return "Unexpected error: PageSpeed result was not returned by the API.";
  }

  const { categories, audits } = data.lighthouseResult;

  const score = (cat) => {
    if (!cat || cat.score == null) return "N/A";
    return String(Math.round(cat.score * 100));
  };

  return [
    `PageSpeed Insights: ${url} [${strategy}]`,
    `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`,
    `Performance:       ${score(categories.performance)}/100`,
    `Accessibility:     ${score(categories.accessibility)}/100`,
    `Best Practices:    ${score(categories["best-practices"])}/100`,
    `SEO:               ${score(categories.seo)}/100`,
    ``,
    `Core Web Vitals:`,
    `  FCP  (First Contentful Paint):   ${audits["first-contentful-paint"]?.displayValue ?? "N/A"}`,
    `  LCP  (Largest Contentful Paint):  ${audits["largest-contentful-paint"]?.displayValue ?? "N/A"}`,
    `  TBT  (Total Blocking Time):       ${audits["total-blocking-time"]?.displayValue ?? "N/A"}`,
    `  CLS  (Cumulative Layout Shift):   ${audits["cumulative-layout-shift"]?.displayValue ?? "N/A"}`,
    `  SI   (Speed Index):              ${audits["speed-index"]?.displayValue ?? "N/A"}`,
  ].join("\n");
}

// Tool definitions for MCP
const TOOLS = [
  {
    name: "pagespeed_analyze",
    description:
      "Analyze web performance of a URL using Google PageSpeed Insights API. Returns scores for Performance, Accessibility, Best Practices, SEO, and Core Web Vitals (FCP, LCP, TBT, CLS, SI). Use to audit project pages and diagnose loading issues.",
    inputSchema: {
      type: "object",
      properties: {
        url: {
          type: "string",
          description: "Full URL to analyze. Example: https://example.com",
        },
        strategy: {
          type: "string",
          enum: ["mobile", "desktop"],
          default: "mobile",
          description: "Test device: mobile or desktop",
        },
      },
      required: ["url"],
    },
  },
];

// Handle incoming JSON-RPC messages
let buffer = "";

rl.on("line", async (line) => {
  buffer += line;

  // Try to parse complete JSON-RPC message
  try {
    // Skip Content-Length headers
    if (buffer.startsWith("Content-Length:")) {
      buffer = "";
      return;
    }

    const message = JSON.parse(buffer);
    buffer = "";

    const { id, method, params } = message;

    switch (method) {
      case "initialize":
        sendResponse(id, {
          protocolVersion: "2024-11-05",
          capabilities: { tools: {} },
          serverInfo: {
            name: "pagespeed-mcp",
            version: "1.0.0",
          },
        });
        break;

      case "tools/list":
        sendResponse(id, { tools: TOOLS });
        break;

      case "tools/call":
        if (params.name === "pagespeed_analyze") {
          const { url, strategy } = params.arguments || {};
          if (!url) {
            sendError(id, -32602, "Missing required parameter: url");
            return;
          }
          try {
            const result = await analyzePageSpeed(url, strategy || "mobile");
            sendResponse(id, {
              content: [{ type: "text", text: result }],
            });
          } catch (err) {
            sendError(id, -32603, `Analysis failed: ${err.message}`);
          }
        } else {
          sendError(id, -32601, `Unknown tool: ${params.name}`);
        }
        break;

      case "notifications/initialized":
        // Acknowledged, no response needed
        break;

      default:
        if (id !== undefined) {
          sendError(id, -32601, `Method not found: ${method}`);
        }
    }
  } catch {
    // Incomplete JSON, wait for more data
  }
});

process.on("SIGINT", () => process.exit(0));
process.on("SIGTERM", () => process.exit(0));
