---
name: kimi-thermodynamic
description: Thermodynamic execution framework (T*) for LLM query classification and adaptive response. Triggers - T* framework, thermodynamic state, query classification, adaptive temperature.
version: 1.0.0
---

# Kimi Thermodynamic Framework (T*)

## Overview

Canonical thermodynamic execution framework that classifies queries into ACT/HOLD/REFUSE regimes using the T* formula: `T* = (L - γ) / (|L| + λ)`. Automatically adjusts LLM parameters based on query complexity and system state.

## T* Formula

```
T* = (L - γ) / (|L| + λ)

Where:
- L = System coherence (1.5 default, adjusts based on history)
- γ = Query complexity/gamma (estimated from query)
- λ = Lambda base (0.1)
```

## Regimes

| T* Value | Regime | Action |
|----------|--------|--------|
| T* > 0 | **ACT** | Execute normally |
| -1 < T* ≤ 0 | **HOLD** | Auto-ground with search |
| T* ≤ -1 | **REFUSE** | Reject query |

## Implementation Pattern

### 1. State Definition
```python
from dataclasses import dataclass
from enum import Enum

class Regime(Enum):
    ACT = "ACT"
    HOLD = "HOLD"
    REFUSE = "REFUSE"

@dataclass
class ThermoState:
    L: float = 1.5          # Coherence
    gamma: float = 0.5      # Query complexity
    lam: float = 0.1        # Lambda
    T_star: float = 0.0     # Computed T*
    
    def compute(self) -> float:
        denom = abs(self.L) + self.lam
        self.T_star = (self.L - self.gamma) / denom if denom != 0 else float('-inf')
        return self.T_star
    
    def classify(self) -> Regime:
        t = self.compute()
        if t > 0:
            return Regime.ACT
        elif t > -1:
            return Regime.HOLD
        else:
            return Regime.REFUSE
```

### 2. Gamma Estimation
```python
def _estimate_gamma(self, query: str) -> float:
    """Estimate query complexity from features."""
    gamma = 0.3
    
    # Length penalty
    if len(query) > 1000:
        gamma += 0.3
    
    # Complexity keywords
    if any(w in query.lower() for w in ["why", "how", "explain", "compare"]):
        gamma += 0.2
    
    # Question penalty
    if "?" in query:
        gamma += 0.1
    
    return min(gamma, 2.0)
```

### 3. Adaptive Execution
```python
async def execute(self, query: str, mode: str = "auto") -> Dict:
    # 1. Estimate complexity
    gamma = self._estimate_gamma(query)
    state = ThermoState(gamma=gamma)
    
    # 2. Adjust coherence from history
    if self.history:
        recent_success = sum(1 for h in self.history[-3:] if h.get("success"))
        state.L = 0.5 + (recent_success / 3) * 1.5
    
    T_star = state.compute()
    
    # 3. REFUSE check
    if T_star <= -1:
        return {
            "regime": "REFUSE",
            "T_star": T_star,
            "output": f"REFUSE: Query requires γ={gamma:.2f} but L={state.L:.2f}",
        }
    
    # 4. HOLD: Auto-ground
    grounding = None
    if -1 < T_star <= 0:
        grounding = await self._auto_ground(query)
        if grounding:
            state.L = min(2.0, state.L + 0.3)
            T_star = state.compute()
    
    # 5. Adaptive parameters
    if mode == "benchmark":
        temp, top_p = 1.0, 0.95
        max_tokens = 128000
    else:
        temp = max(0.1, min(1.0, (T_star + 1) / 2))
        max_tokens = 8192 if T_star > 0.5 else 4096
    
    # 6. Execute with thermodynamic system prompt
    system = self._assemble_prompt(T_star, grounding)
    # ... LLM call ...
    
    # 7. Update thermodynamics
    success = len(full_response) > 50
    state.L = state.L * 1.05 if success else state.L * 0.95
    entropy = state.L - gamma
    self.current_entropy += max(0, -entropy)
    
    return {
        "output": full_response,
        "regime": "ACT" if T_star > 0 else "HOLD",
        "T_star": T_star,
        "entropy": self.current_entropy,
    }
```

### 4. Auto-Grounding
```python
async def _auto_ground(self, query: str) -> Optional[str]:
    """Fetch grounding context via web search."""
    try:
        resp = await self.http.post(
            "/formulas/moonshot/web-search:latest/fibers",
            json={"name": "web_search", "arguments": json.dumps({"query": query[:100]})}
        )
        if resp.json().get("status") == "succeeded":
            return resp.json()["context"].get("output", "")[:500]
    except:
        pass
    return None
```

## Rules

### Do
- Estimate gamma from query features (length, keywords, questions)
- Adjust L based on recent success rate
- Auto-ground on HOLD regime
- Scale temperature with T*: `temp = (T* + 1) / 2`
- Track entropy budget
- Update L after each execution (±5%)

### Don't
- Skip REFUSE check before execution
- Use fixed temperature regardless of T*
- Ignore grounding failures
- Let entropy grow unbounded
- Hardcode gamma values

## Display Format

```python
def _regime_display(regime: str) -> str:
    if regime == "ACT":
        return "🟢 ACT"
    if regime == "HOLD":
        return "🟡 HOLD"
    return "🔴 REFUSE"

def _health_color(score: int) -> str:
    if score >= 80:
        return "\033[92m"  # Green
    if score >= 60:
        return "\033[93m"  # Yellow
    return "\033[91m"      # Red
```

## File Location
- `kimi_thermo/thermo_executor.py` - Core implementation
- `kimi_thermo/complete_cli.py` - CLI with thermodynamic display

<!-- Generated by skill-master command
Version: 1.0.0
Sources:
- kimi_thermo/thermo_executor.py
- kimi_thermo/complete_cli.py
Last updated: 2026-03-20
-->
