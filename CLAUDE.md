# Project rules — Python / FastAPI backend

These rules apply to all Python code written or edited in this repo.

1. **Type hints on every function signature, including returns.**
   No untyped `def` — parameters and return type must be annotated.

2. **Validate request/response bodies with Pydantic models — never raw `dict`.**
   Every endpoint's input/output shape must be a Pydantic model, not a bare `dict` or `**kwargs`.

3. **No bare `except:` and no silently swallowed exceptions.**
   Catch specific exception types. Log with `logger.exception(...)` and re-raise unless there's a documented reason not to.

4. **Config/secrets via `pydantic-settings`, never hardcoded.**
   No hardcoded URLs, credentials, or API keys in source. Read from a `Settings(BaseSettings)` class backed by env vars.

5. **Structured logging, not `print()`.**
   Use the `logging` module (`logger.info(...)`, `logger.exception(...)`) with contextual fields, never `print()`.

6. **DB sessions via dependency injection, not module-level globals.**
   Use a `get_db()` generator dependency (`Depends(get_db)`) that yields a session and closes it. Never create a session at import time and share it across requests.

7. **Centralized error handling with a custom exception hierarchy.**
   Raise domain exceptions (subclasses of a shared `AppError`) instead of `HTTPException` inline in route handlers. Register one exception handler that maps them to responses.

8. **Never call blocking/sync I/O inside `async def`.**
   No `requests`, `time.sleep`, or other blocking calls inside async routes/functions. Use `httpx.AsyncClient` (or `await asyncio.sleep`) instead.

9. **Tests follow arrange-act-assert, no `time.sleep` for waits.**
   Use fixtures and polling/condition helpers instead of fixed sleeps to wait for async state.

10. **Tooling is a hard gate — ruff and mypy must be clean before a task is done.**
    After any code change, run `ruff check --fix .`, `ruff format .`, and `mypy .`. Resolve everything they report. Do not suppress with `# noqa` or `# type: ignore` just to force a pass — fix the underlying issue, or ask before suppressing. A task is not complete while these fail.
