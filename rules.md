# Project Rules - Market Analyst

These rules must be followed strictly throughout the development process:

1.  **Mandatory Testing**: Every piece of code (functions, flows, agents) must have corresponding unit or integration tests.
2.  **Comprehensive Logging**: All functions and flows must implement logging. Logs should be directed to a `dump.log` file to track execution and debug issues.
3.  **Mocking for Tests**: Never make real API calls (Yahoo Finance, DuckDuckGo, Groq, Gemini) during tests. Always use mocks to simulate API responses to preserve free-tier quotas and ensure deterministic testing.
