# Task 2: Testing MCP Servers — Playwright vs. Chrome DevTools

Deliverable for "AI-Driven Development Tools for Software Engineers" — Task 2
(Test MCP Servers for Your Workflow).

## What this is

Two MCP servers installed and exercised against a real practical scenario:
manually testing the `POST /orders` endpoint from [Task 1](./README.md)
through its FastAPI Swagger UI (`/docs`), the way a backend dev checks a new
endpoint end-to-end before writing an automated test for it.

- **Playwright MCP** (`@playwright/mcp`) — general browser automation
- **Chrome DevTools MCP** (`chrome-devtools-mcp`) — browser automation +
  DevTools introspection (network, console, performance)

Both were added via `claude mcp add <name> --scope user -- npx <package>@latest`
(user scope, so they're available regardless of the exact project path).

## Setup

```
py -3.11 -m venv .venv
.venv\Scripts\pip install fastapi uvicorn pydantic pydantic-settings sqlalchemy
PYTHONPATH=. .venv/Scripts/python.exe scripts/seed_dev_data.py   # creates tables + one customer
PYTHONPATH=. .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
```

`scripts/seed_dev_data.py` just calls `Base.metadata.create_all()` and inserts
one `Customer(id=1)` so `POST /orders` has a real row to reference — it's a
throwaway dev aid, not part of the app.

## Test 1 — Playwright MCP

Opened `/docs`, expanded `POST /orders`, clicked "Try it out", and ran two
requests through Swagger's built-in "Execute":

**Valid customer:**
```
Request:  { "customer_id": 1, "item_count": 3 }
Response: 201 { "id": 1, "customer_id": 1, "item_count": 3 }
```

**Nonexistent customer** (exercises the `CustomerNotFoundError` → `AppError`
handler from Task 1's rule 7):
```
Request:  { "customer_id": 999, "item_count": 2 }
Response: 404 { "error": "Customer 999 not found" }
```

`browser_network_requests` confirmed both status codes in one call:
```
6. [POST] http://127.0.0.1:8000/orders => [201] Created
7. [POST] http://127.0.0.1:8000/orders => [404] Not Found
```

`browser_console_messages` also picked up the browser's own console log for
the failed fetch (`Failed to load resource: 404`) — useful, but it's the
browser's message, not the response body.

### What it does well
- `browser_snapshot` returns a clean accessibility tree with stable element
  refs (`ref=e186` etc.) — reliable for clicking/filling without brittle CSS
  selectors, and it correctly recognized Swagger's code editor as a single
  `textbox` node.
- Fast to install and drive — no auth, one `npx` command.
- `browser_network_requests` is a good quick pass/fail signal (status codes
  at a glance) for scripted user-flow style checks.

### Limitations
- Network detail is a summary line, not full headers/body — you'd still open
  DevTools (or use Chrome DevTools MCP) to see the actual JSON payload sent
  over the wire; here we only saw it because Swagger UI itself echoes it in
  the page.
- No performance/profiling angle — it's an automation tool, not a debugging
  one.

### Recommended use cases
- Scripted end-to-end / UI regression flows (login, form submission,
  multi-step wizards).
- Driving a UI to *set up state* for a subsequent API or DB check.

## Test 2 — Chrome DevTools MCP

Repeated the same interaction on a fresh page, but used it to inspect what
actually crossed the wire and how the page loaded:

`take_snapshot` before clicking "Try it out" exposed the CodeMirror example
block as a flat list of `StaticText` nodes (`"customer_id"`, `": "`, `"0"`, …)
rather than one text block — noisier than Playwright's snapshot for this
particular widget, though it became a proper `textbox` once "Try it out" was
clicked, same as Playwright.

**Full request detail**, one call, for the `POST /orders` request:
```
get_network_request(reqid=7)
Status: 201
Request Headers: content-type: application/json, accept: application/json, ...
Request Body:  { "customer_id": 1, "item_count": 5 }
Response Headers: content-length: 39, content-type: application/json, ...
Response Body: {"id":2,"customer_id":1,"item_count":5}
```
This is the actual bytes sent/received — no dependence on the page echoing
it back, unlike the Playwright test above.

**Performance trace** of the `/docs` page load (`performance_start_trace`,
`reload: true`, `autoStop: true`):
```
LCP: 419 ms  (TTFB: 2 ms, Render delay: 417 ms)
CLS: 0.51
Insights available: LCPBreakdown, CLSCulprits, RenderBlocking,
                     NetworkDependencyTree, ThirdParties, Cache
```
Swagger UI's own React re-renders after load account for the CLS score —
not something you'd normally chase on an internal docs page, but this shows
the tool would flag a real layout-shift regression on a customer-facing page.

### What it does well
- `get_network_request` gives complete request/response headers and bodies
  in one call — the right tool when you need to *prove* what an endpoint
  actually received or returned, not just its status code.
- `performance_start_trace` / `performance_analyze_insight` surface Core Web
  Vitals (LCP/CLS) and named, actionable insights out of the box — genuinely
  useful for debugging a slow page, which Playwright doesn't attempt.
- Also connected to a real local Chrome, so it's the same tool a frontend/perf
  engineer already reaches for in the browser DevTools, just scriptable.

### Limitations
- Accessibility snapshots are noisier for widgets built from many small text
  nodes (saw this on Swagger's syntax-highlighted JSON block).
- Performance/network tooling is overkill for a pure backend contract check —
  most of what it reports (LCP, CLS) doesn't apply to an API with no
  meaningful UI.

### Recommended use cases
- Debugging a slow or failing request end-to-end (headers, timing, payload)
  when a bug report is vague ("the request just hangs").
- Frontend performance regressions — Core Web Vitals, render-blocking
  resources, layout shift culprits.

## Comparison

| | Playwright MCP | Chrome DevTools MCP |
|---|---|---|
| Setup | `npx @playwright/mcp`, no auth | `npx chrome-devtools-mcp`, no auth |
| Best for | Scripting user flows | Debugging what happened on the wire |
| Network detail | Status + URL summary | Full headers + request/response body |
| Performance | None | LCP/CLS/trace insights |
| Snapshot quality | Consistently clean refs | Can be noisy on custom widgets |

## Recommendation

For this Python/FastAPI backend role, neither replaces `pytest` + `httpx` for
routine endpoint tests, but both earn a place for the cases automated tests
don't cover well:

- **Chrome DevTools MCP** for the "why is this request behaving oddly"
  investigations — the full request/response capture in one call
  (`get_network_request`) is the standout feature.
- **Playwright MCP** for the "does the whole flow still work" checks,
  especially once there's an actual frontend in front of the API rather than
  just Swagger UI.

## Repo layout

```
MCP_SERVERS.md          this document
scripts/
  seed_dev_data.py       dev-only helper: create tables + one Customer row
```
