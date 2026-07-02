import asyncio
import time
import inspect
from enum import Enum
from typing import Callable, Any, Dict
import logging

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

class ModuleState:
    def __init__(self):
        self.state = CircuitState.CLOSED
        self.failures = 0
        self.cooldown_until = 0
        
        # Metrics
        self.execution_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.timeout_count = 0
        self.retry_count = 0
        self.total_latency = 0.0
        self.last_success = None
        self.last_error = None
        
    @property
    def avg_latency(self):
        if self.success_count == 0:
            return 0.0
        return round(self.total_latency / self.success_count, 3)

_MODULES: Dict[str, ModuleState] = {}
CIRCUIT_THRESHOLD = 5
CIRCUIT_COOLDOWN = 60 # seconds

def _get_module(name: str) -> ModuleState:
    if name not in _MODULES:
        _MODULES[name] = ModuleState()
    return _MODULES[name]

def register_module(name: str):
    """Pre-register an AI module so it appears in health checks before first invocation."""
    _get_module(name)

def _log_event(module_name: str, event: str, latency: float = 0, **kwargs):
    # Simple structured logging
    args_str = " | ".join(f"{k}: {v}" for k,v in kwargs.items())
    msg = f"[{event}] Module: {module_name} | Latency: {latency:.3f}s"
    if args_str:
        msg += f" | {args_str}"
    print(msg)

async def execute_resilient(
    module_name: str,
    func: Callable,
    *args,
    fallback: Any = None,
    timeout: float = 5.0,
    retries: int = 1,
    **kwargs
) -> Any:
    """
    Executes an AI module function with resilience:
    - Circuit Breaker pattern
    - Timeouts (both for async and sync functions)
    - Retries (transient errors)
    - Graceful degradation (returns fallback on failure)
    - Emits structured telemetry
    """
    state = _get_module(module_name)
    
    # Check Circuit Breaker
    if state.state == CircuitState.OPEN:
        if time.time() > state.cooldown_until:
            state.state = CircuitState.HALF_OPEN
            _log_event(module_name, "AI_MODULE_CIRCUIT_HALF_OPEN")
        else:
            state.execution_count += 1
            return fallback

    is_async = inspect.iscoroutinefunction(func)
    
    _log_event(module_name, "AI_MODULE_STARTED")
    
    for attempt in range(retries + 1):
        state.execution_count += 1
        start_time = time.time()
        try:
            if is_async:
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            else:
                loop = asyncio.get_running_loop()
                # Use default executor to run synchronous AI tasks to prevent loop blocking
                # Using wrapper lambda to avoid kwarg unpacking issues in run_in_executor
                def _sync_wrapper():
                    return func(*args, **kwargs)
                coro = loop.run_in_executor(None, _sync_wrapper)
                result = await asyncio.wait_for(coro, timeout=timeout)
                
            latency = time.time() - start_time
            state.success_count += 1
            state.total_latency += latency
            state.last_success = time.time()
            
            # Reset circuit
            if state.state != CircuitState.CLOSED:
                state.state = CircuitState.CLOSED
                state.failures = 0
                _log_event(module_name, "AI_MODULE_RECOVERED", latency=latency)
                
            _log_event(module_name, "AI_MODULE_COMPLETED", latency=latency)
            return result
            
        except (asyncio.TimeoutError, TimeoutError):
            latency = time.time() - start_time
            state.timeout_count += 1
            _log_event(module_name, "AI_MODULE_TIMEOUT", latency=latency, attempt=attempt+1)
            state.last_error = "Timeout"
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            latency = time.time() - start_time
            state.failure_count += 1
            state.last_error = str(e)
            _log_event(module_name, "AI_MODULE_FAILED", latency=latency, attempt=attempt+1, error=str(e))
            
            # Do not retry validation or missing input errors
            if isinstance(e, (ValueError, TypeError, KeyError)):
                break
                
        # Wait before retry
        if attempt < retries:
            state.retry_count += 1
            _log_event(module_name, "AI_MODULE_RETRY", latency=time.time() - start_time, attempt=attempt+1)
            await asyncio.sleep(0.5)

    # Failed completely
    state.failures += 1
    if state.failures >= CIRCUIT_THRESHOLD:
        state.state = CircuitState.OPEN
        state.cooldown_until = time.time() + CIRCUIT_COOLDOWN
        _log_event(module_name, "AI_MODULE_CIRCUIT_OPEN", latency=time.time() - start_time)
        
    return fallback

def get_ai_health() -> dict:
    modules = []
    for name, state in _MODULES.items():
        total = state.success_count + state.failure_count + state.timeout_count
        success_rate = round((state.success_count / total) * 100, 1) if total > 0 else 100.0
        modules.append({
            "name": name,
            "status": "Healthy" if state.state == CircuitState.CLOSED else ("Degraded" if state.state == CircuitState.HALF_OPEN else "Offline"),
            "latency_ms": round(state.avg_latency * 1000, 1),
            "success_rate": success_rate,
            "circuit": state.state.value,
            "invocations": total,
            "failures": state.failure_count,
            "timeouts": state.timeout_count,
            "last_error": state.last_error
        })
    return {"modules": modules}

def reset_circuit_breaker(module_name: str):
    if module_name in _MODULES:
        _MODULES[module_name].state = CircuitState.CLOSED
        _MODULES[module_name].failures = 0

def get_module_metrics(module_name: str) -> dict:
    if module_name in _MODULES:
        state = _MODULES[module_name]
        return {
            "execution_count": state.execution_count,
            "success_count": state.success_count,
            "failure_count": state.failure_count,
            "retry_count": state.retry_count,
            "timeout_count": state.timeout_count,
            "avg_latency": state.avg_latency
        }
    return {}
