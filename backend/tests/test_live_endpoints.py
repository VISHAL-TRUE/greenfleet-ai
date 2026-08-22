"""
GreenFleet AI — Live Endpoint Smoke Tests
==========================================
Exercises every registered API endpoint against a running uvicorn server.
Run with:  python backend/tests/test_live_endpoints.py
"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8000"

ok: list = []
fail: list = []


def get(path: str):
    try:
        r = urllib.request.urlopen(BASE + path, timeout=15)
        data = json.loads(r.read())
        ok.append(("GET ", path, r.getcode()))
        return data
    except Exception as e:
        fail.append(("GET ", path, str(e)[:100]))
        return None


def post(path: str, body: dict):
    try:
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        r = urllib.request.urlopen(req, timeout=20)
        data = json.loads(r.read())
        ok.append(("POST", path, r.getcode()))
        return data
    except urllib.error.HTTPError as e:
        detail = e.read()[:120].decode(errors="replace")
        fail.append(("POST", path, f"HTTP {e.code}: {detail}"))
        return None
    except Exception as e:
        fail.append(("POST", path, str(e)[:100]))
        return None


# ── Health ─────────────────────────────────────────────────────────────────
get("/")
get("/health")

# ── Fleet ──────────────────────────────────────────────────────────────────
vehicles = get("/api/fleet/vehicles")
routes   = get("/api/fleet/routes")

# ── Prediction ─────────────────────────────────────────────────────────────
if vehicles and routes:
    post("/api/predict/batch", {
        "pairs": [{"vehicle": vehicles[0], "route": routes[0]}]
    })

# ── Optimization ───────────────────────────────────────────────────────────
if vehicles and routes:
    post("/api/optimize/assign", {
        "vehicles": vehicles[:3],
        "routes": routes[:2],
        "objective": "balanced",
    })

# ── Simulation run ─────────────────────────────────────────────────────────
post("/api/simulate/run", {
    "scenario": "normal",
    "traffic_multiplier": 1.0,
    "payload_multiplier": 1.0,
})
post("/api/simulate/run", {
    "scenario": "peak_demand",
    "traffic_multiplier": 1.0,
    "payload_multiplier": 1.25,
})
get("/api/simulate/benchmarks/summary")

# ── Simulation lifecycle ────────────────────────────────────────────────────
post("/api/simulate/reset", {})
post("/api/simulate/peak", {})
post("/api/simulate/traffic", {})
post("/api/simulate/optimize", {})
get("/api/simulate/state")

# ── Benchmark ──────────────────────────────────────────────────────────────
get("/api/benchmark")

# ── Forecast ───────────────────────────────────────────────────────────────
if vehicles and routes:
    post("/api/forecast", {
        "vehicles": vehicles[:2],
        "routes": routes[:2],
    })

# ── Results ────────────────────────────────────────────────────────────────
print("\n=== PASSED ===")
for m, p, code in ok:
    print(f"  {m} {p:<50} [{code}]")

if fail:
    print("\n=== FAILED ===")
    for m, p, err in fail:
        print(f"  {m} {p:<50} -> {err}")
else:
    print("\nAll endpoints OK!")

print(f"\nSummary: {len(ok)} passed, {len(fail)} failed")
sys.exit(0 if not fail else 1)
