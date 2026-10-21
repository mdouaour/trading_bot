# Repository Audit and Architecture Plan (Phase 0)

Date: 2026-10-21  
Repository: `mdouaour/trading_bot`  
Branch audited: `copilot/build-automated-xauusd-platform`

## 1. Repository Audit

- Current tracked files:
  - `/home/runner/work/trading_bot/trading_bot/README.md`
- Current codebase status:
  - No application code exists yet.
  - No Python package, Node app, or monorepo layout exists.
  - No tests, CI definitions, infrastructure config, migrations, or runtime configs exist.
- Git history:
  - `Initial commit`
  - `Initial plan`
- CI status checked:
  - Workflow run exists (`Running Copilot cloud agent`).
  - Failed job logs: none (`No failed jobs found`).

## 2. Existing Architecture

- There is no implemented software architecture yet.
- Repository is effectively a blank initialization state with a single README.

## 3. Existing Components Worth Keeping

- Keep the repository itself and branch workflow.
- Keep `README.md` as project root entrypoint (to expand, not replace).

## 4. Problems / Risks

- No deterministic trading pipeline exists.
- No risk firewall, OMS, reconciliation, or broker abstraction exists.
- No point-in-time data controls exist.
- No typed config / secrets management standards are defined.
- No tests, no lint/type gates, no observability, no audit trail.
- Highest immediate risk: accidental ad hoc implementation without architectural guardrails.

## 5. Missing Components

All required platform components are missing, including:

- Data ingestion and point-in-time layer
- Feature engine
- Strategies and ML/regime components
- Signal aggregator
- Portfolio sizing and risk firewall
- OMS and MT5 adapter
- Position management and reconciliation
- Backtesting and research validation
- API, monitoring, dashboard, and audit logging
- CI/CD quality and security checks

## 6. Target Architecture

Use modular monolith first, with strict separation:

- Alpha generation (strategy/ML)
- Portfolio sizing
- Risk firewall (fail-closed)
- Execution (OMS + broker adapter)
- Infrastructure (data, persistence, monitoring)

Hard rule:
- Strategy/LLM can emit signals only.
- Only OMS after risk approval can submit broker orders.

## 7. Proposed Repository Structure

Proposed initial structure adapted from target:

- `apps/api/`
- `apps/worker/`
- `apps/dashboard/`
- `packages/trading_core/` with domains:
  - `core`, `data`, `features`, `strategies`, `models`, `portfolio`, `risk`, `execution`, `brokers`, `research`, `monitoring`, `intelligence`
- `configs/`
- `migrations/`
- `tests/{unit,integration,backtest,risk,execution,parity}/`
- `docs/`
- `infra/`

## 8. Dependency Assessment

Current:
- No dependency manager configured.
- No lockfiles.
- No Python or Node runtime constraints defined.

Recommended baseline:
- Python 3.12+
- FastAPI, Pydantic, SQLAlchemy, Alembic, psycopg, Redis client
- Polars, NumPy, pandas (limited), scikit-learn, XGBoost, hmmlearn
- pytest, mypy, ruff
- structlog, httpx
- Optional frontend: Next.js + TypeScript + Tailwind

## 9. Security Assessment

Current security posture:
- No application attack surface yet (no code/endpoints).
- No secret management policy implemented in code/config.

Required controls from day 1:
- `.env.example` only, never commit real secrets
- Input validation and schema enforcement
- AuthN/AuthZ for administrative endpoints
- Secret-safe logging
- Dependency and static security checks in CI

## 10. Trading-System Safety Assessment

Current safety posture:
- Safety mechanisms absent because trading engine is not implemented.

Required non-negotiable safety controls:
- Risk firewall before any order submission
- Kill switch
- Stale-data guard
- Exposure/drawdown/daily-loss limits
- Idempotent order handling + reconciliation
- Fail-closed behavior on uncertainty

## 11. Implementation Roadmap

- **Phase 0**: audit + architecture + ADRs (current phase)
- **Phase 1**: core domain contracts/types/events
- **Phase 2**: point-in-time data ingestion and validation
- **Phase 3**: feature engine (timestamp-safe)
- **Phase 4**: realistic event-driven backtester
- **Phase 5**: baseline deterministic strategies
- **Phase 6**: portfolio sizing
- **Phase 7**: risk firewall
- **Phase 8**: OMS state machine + idempotency
- **Phase 9**: MT5 adapter abstraction/implementation
- **Phase 10+**: paper trading, ML/regime, intelligence, dashboard, hardening

## 12. Phase 1 Exact Tasks

1. Create project skeleton and package boundaries.
2. Define canonical domain models (`Signal`, `Order`, `Position`, `RiskDecision`, `Quote`, `MarketBar`, `EconomicEvent`).
3. Define lifecycle enums/state machines (orders/positions).
4. Define interfaces/contracts:
   - `Strategy`
   - `SignalAggregator`
   - `PositionSizer`
   - `RiskFirewall`
   - `BrokerAdapter`
   - `OrderManager`
5. Add typed settings/config module with risk defaults and environment loading.
6. Add structured logging bootstrap.
7. Add initial unit tests for core models/state transitions.

## 13. Files Recommended for Creation/Modification

Immediate (Phase 0/1 planning):
- Modify `/home/runner/work/trading_bot/trading_bot/README.md` (project scope and principles)
- Create `/home/runner/work/trading_bot/trading_bot/docs/repository_audit.md` (this file)
- Create `/home/runner/work/trading_bot/trading_bot/docs/architecture.md`
- Create `/home/runner/work/trading_bot/trading_bot/docs/phase_plan.md`

Phase 1 implementation (after approval):
- `pyproject.toml`
- `apps/api/...`
- `apps/worker/...`
- `packages/trading_core/...`
- `tests/unit/...`

## 14. Tests Required

Minimum Phase 1 tests:
- Domain model validation tests (Pydantic/type rules)
- Enum/lifecycle transition tests for orders and positions
- Contract/interface conformance smoke tests
- Timezone-aware timestamp tests (UTC required)

Future critical tests:
- Leakage prevention tests (point-in-time correctness)
- Risk firewall rejection/adjustment tests
- OMS idempotency and restart-recovery tests
- Parity tests (backtest vs paper/live decision pipeline)

## 15. Open Questions / Assumptions

1. Confirm backend-first approach (Python monolith first, dashboard later).
2. Confirm whether to bootstrap frontend now or defer to Phase 15.
3. Confirm target deployment OS and MT5 connectivity model (native terminal/bridge).
4. Confirm initial data providers for XAUUSD bars/ticks, macro events, and news.
5. Confirm initial risk limits and trading sessions policy.
6. Confirm whether PostgreSQL/Redis should be added in Phase 1 or Phase 2.
7. Confirm CI provider and minimum required quality gates.

---

Status: Phase 0 audit complete.  
Per requirement, major architectural implementation should wait for approval.
