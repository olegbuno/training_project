# Task 1: Custom Ruleset for a Python/FastAPI Backend

Deliverable for "AI-Driven Development Tools for Software Engineers" — Task 1
(Rules, Skills, Custom Agents).

## What this is

A `CLAUDE.md` at the repo root with 10 rules tailored to a Python/FastAPI
backend, plus a live before/after test showing the rules actually change
agent behavior — not just a written policy nobody follows.

## The rules

See [`CLAUDE.md`](./CLAUDE.md) for the full text. Summary:

1. Type hints on every function signature, including returns.
2. Validate request/response bodies with Pydantic models — never raw `dict`.
3. No bare `except:` and no silently swallowed exceptions.
4. Config/secrets via `pydantic-settings`, never hardcoded.
5. Structured logging, not `print()`.
6. DB sessions via dependency injection, not module-level globals.
7. Centralized error handling with a custom exception hierarchy.
8. Never call blocking/sync I/O inside `async def`.
9. Tests follow arrange-act-assert, no `time.sleep` for waits.
10. Tooling is a hard gate — `ruff` and `mypy` must be clean before a task
    is considered done.

Rules 1–9 shape *what the code looks like*. Rule 10 is different in kind:
it doesn't describe a style, it forces a verification step the agent
otherwise skips — "write code" and "write code, then prove it's clean"
are different tasks.

## Why these rules

Style rules (line length, quote style, import order) were deliberately
**left out** — a formatter enforces those deterministically and better
than prose instructions ever could. The 10 rules above target things a
formatter/linter alone won't catch and that recur across most backend
codebases: raw-dict payloads, swallowed exceptions, print-based logging,
leaking DB sessions, inconsistent error responses, blocking calls in
async code, and flaky sleep-based tests.

## Before/after test

Same task given twice: *"add a `POST /orders` endpoint."*

- [`demo/before_orders.py`](./demo/before_orders.py) — representative output
  without the rules: raw `dict` in/out, in-memory list instead of the DB,
  `print()` logging, bare `except`, no types.
- [`demo/after_orders.py`](./demo/after_orders.py) — a copy of the **actual
  output of a fresh subagent** instructed only to read `CLAUDE.md` and
  implement the same feature. The live version is wired into the app at
  [`app/schemas.py`](./app/schemas.py) and [`app/orders.py`](./app/orders.py).

The after-version reflects rules 1, 2, 3 (via the exception hierarchy), 4
(existing `Settings`/`get_db` conventions it used correctly), 5, 6, 7, and
10 — it added a `Depends(get_db)` session, a Pydantic `OrderCreate`/`OrderRead`
pair, a `CustomerNotFoundError` domain exception instead of an inline
`HTTPException`, structured `logger.info(...)` calls, and full type hints.

For rule 10, the agent didn't just claim the gate passed — `ruff` and
`mypy` weren't on the default PATH, so it located an interpreter that had
them, installed the missing packages, ran `ruff check --fix .`,
`ruff format .`, and `mypy .`, and fixed a real `ruff` false-positive on
`Depends(get_db)` via a `pyproject.toml` config change rather than a
`# noqa` suppression — matching rule 10's "fix the underlying issue, don't
suppress" instruction.

## Inspiration

- [awesome-cursorrules](https://github.com/PatrickJS/awesome-cursorrules) —
  community `.cursorrules` examples, including Python/FastAPI and Django
  ones, useful for seeing how other teams phrase these as directives.
- [skills.sh](https://skills.sh) — a marketplace of packaged, invokable
  *skills* rather than passive rules; worth exploring if a rule should
  become a runnable workflow instead of a standing instruction.

## Repo layout

```
CLAUDE.md              the 10 rules
pyproject.toml         ruff + mypy config the rules point to
app/
  main.py              FastAPI app, registers the AppError exception handler
  config.py            pydantic-settings Settings
  database.py          engine, SessionLocal, get_db dependency
  models.py            Customer, Order (SQLAlchemy)
  schemas.py           OrderCreate, OrderRead (Pydantic) — agent-generated
  exceptions.py        AppError, CustomerNotFoundError
  orders.py            POST /orders — agent-generated, follows all 10 rules
demo/
  before_orders.py     illustrative baseline without the rules
  after_orders.py       copy of the actual rule-compliant agent output
```
