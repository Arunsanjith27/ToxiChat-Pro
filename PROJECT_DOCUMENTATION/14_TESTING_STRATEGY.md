# Testing Strategy

Due to the stochastic nature of Machine Learning models and the stateful nature of WebSockets, testing ToxiChat Pro requires a multi-layered approach that goes beyond standard CRUD application testing.

## 1. Unit Testing
Framework: `pytest` and `pytest-asyncio`.
- **Target**: Pure functions in `security.py`, `compliance.py`, and `risk_engine.py`.
- **Strategy**: Test deterministic logic. For example, `risk_engine.calculate_message_risk` must be tested against a matrix of mock `tox_data` objects to ensure it always returns `CRITICAL` when `nsfw_score > 0.6`.
- **Mocking**: Database calls (`motor`) and ML models are strictly mocked using `unittest.mock`.

## 2. Integration Testing
Framework: `pytest` with `httpx` (AsyncTestClient).
- **Target**: FastAPI routers (`auth_router.py`, `main.py` REST endpoints).
- **Strategy**: Spin up the FastAPI application connected to an ephemeral test database. Execute end-to-end HTTP calls (e.g., Register -> Login -> Get Token -> Call `/api/me`).
- **Data State**: The database is dropped and recreated between test suites.

## 3. Machine Learning Regression Testing
- **Target**: The `ai/` pipelines.
- **The Challenge**: Updating a model (e.g., from RoBERTa v1 to v2) might fix a false negative but introduce false positives.
- **Strategy**: A dedicated "Golden Dataset" of 1,000 carefully labeled toxic and non-toxic messages resides in the repo. Before any ML service is deployed, it must run inference on the Golden Dataset. If the F1-Score or Recall drops below the baseline, the CI pipeline fails.

## 4. WebSocket & Concurrency Testing
- **Target**: `ConnectionManager` and Redis Pub/Sub.
- **Strategy**: Use specialized tooling (e.g., `locust` or `artillery`) to simulate 500 concurrent WebSocket connections. Test payload fan-out by having one connection broadcast to a Group containing the other 499 connections, measuring the latency from `send` to the 499th `receive`.

## 5. End-to-End (E2E) UI Testing
Framework: `Cypress` or `Playwright`.
- **Target**: React Frontend.
- **Strategy**: Automate user journeys:
  1. Log in as an Admin.
  2. Upload an image to the Evidence Inspector.
  3. Verify the Canvas overlays the OCR text correctly.
  4. Generate and download a PDF report.
  5. Log in as a User. Type a toxic message. Verify the orange Pre-Send AI Warning modal appears.

## 6. Continuous Integration (CI) Pipeline
1. **Linting & Formatting**: `flake8` and `black` (Backend), `eslint` and `prettier` (Frontend).
2. **Security Scanning**: `bandit` for Python AST vulnerabilities, `npm audit` for frontend CVEs.
3. **Automated Testing**: Run `pytest`.
4. **Build Verification**: Run `npm run build` to ensure the React app compiles without errors.
