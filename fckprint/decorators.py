"""
fckprint.decorators - Advanced debugging decorators

This module provides specialized decorators that extend fckprint's debugging
capabilities for production environments, performance monitoring, security,
and operational intelligence.

Copyright 2025 SRSWTI Research Labs."""

import time
import functools
import traceback
import os
import sys
import json
import threading
import inspect
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Union
from dataclasses import dataclass, field

# Try to import optional dependencies
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

from .tracer import Tracer as snoop


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

def performance_monitor(threshold: float = 1.0, memory_threshold: int = 100):
    """
    Monitor function performance and memory usage.
    
    Args:
        threshold: Maximum execution time in seconds before warning
        memory_threshold: Maximum memory usage in MB before warning
    
    Example:
        @fckprint.performance_monitor(threshold=0.5, memory_threshold=200)
        def expensive_function():
            # Function will be monitored for performance issues
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('execution_time', 'memory_usage', 'performance_warning'))
        def wrapper(*args, **kwargs):
            if not HAS_PSUTIL:
                execution_time = 0
                memory_usage = 0
                performance_warning = ["PSUTIL_NOT_AVAILABLE"]
                
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold:
                    performance_warning = [f"SLOW: {execution_time:.2f}s > {threshold}s"]
                else:
                    performance_warning = ["OK"]
                
                return result
            
            # Get process for memory monitoring
            process = psutil.Process()
            
            # Record start metrics
            start_time = time.time()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate metrics
                execution_time = time.time() - start_time
                end_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage = end_memory - start_memory
                
                # Performance warnings
                performance_warning = []
                if execution_time > threshold:
                    performance_warning.append(f"SLOW: {execution_time:.2f}s > {threshold}s")
                if memory_usage > memory_threshold:
                    performance_warning.append(f"HIGH_MEMORY: {memory_usage:.2f}MB > {memory_threshold}MB")
                
                if not performance_warning:
                    performance_warning = ["OK"]
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                memory_usage = process.memory_info().rss / 1024 / 1024 - start_memory
                performance_warning = [f"ERROR: {str(e)}"]
                raise
                
        return wrapper
    return decorator


# ============================================================================
# ERROR TRACKING & RETRY LOGIC
# ============================================================================

def error_tracker(log_file: str = "fckprint_errors.log", max_retries: int = 0):
    """
    Track and log errors with optional retry logic.
    
    Args:
        log_file: Path to error log file
        max_retries: Number of retry attempts (0 = no retries)
    
    Example:
        @fckprint.error_tracker(max_retries=3, log_file="api_errors.log")
        def api_call():
            # Function will retry up to 3 times on failure
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('attempt', 'error_type', 'error_message', 'retry_success'))
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    retry_success = attempt > 0
                    if retry_success:
                        print(f"✅ Function '{func.__name__}' succeeded on attempt {attempt + 1}")
                    return result
                    
                except Exception as e:
                    error_type = type(e).__name__
                    error_message = str(e)
                    
                    # Log error
                    timestamp = datetime.now().isoformat()
                    error_log = {
                        'timestamp': timestamp,
                        'function': func.__name__,
                        'attempt': attempt + 1,
                        'error_type': error_type,
                        'error_message': error_message,
                        'args': str(args)[:100],  # Truncate for brevity
                        'kwargs': str(kwargs)[:100]
                    }
                    
                    try:
                        with open(log_file, 'a') as f:
                            f.write(json.dumps(error_log) + '\n')
                    except Exception:
                        pass  # Don't fail if logging fails
                    
                    if attempt == max_retries:
                        retry_success = False
                        print(f"❌ Function '{func.__name__}' failed after {max_retries + 1} attempts")
                        raise
                    else:
                        print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        
        return wrapper
    return decorator


# ============================================================================
# CACHE MONITORING
# ============================================================================

def cache_monitor(cache_size: int = 100, ttl: int = 300):
    """
    Monitor function calls with intelligent caching.
    
    Args:
        cache_size: Maximum number of cached results
        ttl: Time-to-live for cached results in seconds
    
    Example:
        @fckprint.cache_monitor(cache_size=50, ttl=600)
        def expensive_computation(x, y):
            # Results will be cached for 10 minutes
            return x * y
    """
    cache = {}
    cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('cache_key', 'cache_hit', 'cache_stats', 'cache_size_current'))
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            current_time = time.time()
            cache_size_current = len(cache)
            
            # Check cache
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if current_time - timestamp < ttl:
                    cache_hit = True
                    cache_stats['hits'] += 1
                    return cached_data
                else:
                    # Expired
                    del cache[cache_key]
            
            # Cache miss
            cache_hit = False
            cache_stats['misses'] += 1
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            if len(cache) >= cache_size:
                # Evict oldest entry
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]
                cache_stats['evictions'] += 1
            
            cache[cache_key] = (result, current_time)
            
            return result
            
        return wrapper
    return decorator


# ============================================================================
# THREAD SAFETY MONITORING
# ============================================================================

def thread_monitor(max_concurrent: int = 5):
    """
    Monitor thread usage and detect potential race conditions.
    
    Args:
        max_concurrent: Maximum number of concurrent executions before warning
    
    Example:
        @fckprint.thread_monitor(max_concurrent=10)
        def database_operation():
            # Will warn if more than 10 concurrent database operations
            pass
    """
    active_threads = {}
    lock = threading.Lock()
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('thread_id', 'active_count', 'concurrent_warning', 'thread_name'))
        def wrapper(*args, **kwargs):
            thread_id = threading.get_ident()
            thread_name = threading.current_thread().name
            
            with lock:
                active_threads[thread_id] = {
                    'start_time': time.time(),
                    'function': func.__name__,
                    'thread_name': thread_name
                }
                active_count = len(active_threads)
                
                concurrent_warning = []
                if active_count > max_concurrent:
                    concurrent_warning.append(f"HIGH_CONCURRENCY: {active_count} > {max_concurrent}")
                
                # Check for potential race conditions
                same_function_count = sum(1 for t in active_threads.values() 
                                        if t['function'] == func.__name__)
                if same_function_count > 1:
                    concurrent_warning.append(f"RACE_CONDITION_RISK: {same_function_count} instances")
                
                if not concurrent_warning:
                    concurrent_warning = ["OK"]
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                with lock:
                    if thread_id in active_threads:
                        del active_threads[thread_id]
                        
        return wrapper
    return decorator


# ============================================================================
# RESOURCE USAGE MONITORING
# ============================================================================

def resource_monitor(cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
    """
    Monitor system CPU and memory usage during function execution.
    
    Args:
        cpu_threshold: CPU usage percentage threshold for warnings
        memory_threshold: Memory usage percentage threshold for warnings
    
    Example:
        @fckprint.resource_monitor(cpu_threshold=90.0, memory_threshold=85.0)
        def resource_intensive_task():
            # Will warn if system resources are under stress
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('cpu_percent', 'memory_percent', 'resource_warning', 'disk_usage'))
        def wrapper(*args, **kwargs):
            if not HAS_PSUTIL:
                cpu_percent = 0
                memory_percent = 0
                disk_usage = 0
                resource_warning = ["PSUTIL_NOT_AVAILABLE"]
                return func(*args, **kwargs)
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
            disk_usage = psutil.disk_usage('/').percent
            
            resource_warning = []
            if cpu_percent > cpu_threshold:
                resource_warning.append(f"HIGH_CPU: {cpu_percent:.1f}% > {cpu_threshold}%")
            if memory_percent > memory_threshold:
                resource_warning.append(f"HIGH_MEMORY: {memory_percent:.1f}% > {memory_threshold}%")
            if disk_usage > 90:
                resource_warning.append(f"HIGH_DISK: {disk_usage:.1f}%")
            
            if not resource_warning:
                resource_warning = ["OK"]
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# ============================================================================
# DATA VALIDATION
# ============================================================================

def validate_data(input_schema: Dict = None, output_schema: Dict = None):
    """
    Monitor and validate input/output data against schemas.
    
    Args:
        input_schema: Dictionary defining input validation rules
        output_schema: Dictionary defining output validation rules
    
    Example:
        @fckprint.validate_data(
            input_schema={'required_args': 2, 'required_kwargs': ['user_id']},
            output_schema={'type': dict, 'not_none': True}
        )
        def process_user_data(name, email, user_id=None):
            return {'name': name, 'email': email, 'user_id': user_id}
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('input_valid', 'output_valid', 'validation_errors', 'data_size'))
        def wrapper(*args, **kwargs):
            validation_errors = []
            
            # Validate inputs
            input_valid = True
            if input_schema:
                try:
                    # Simple validation (can be extended with jsonschema)
                    if 'required_args' in input_schema:
                        if len(args) < input_schema['required_args']:
                            validation_errors.append(f"Missing args: got {len(args)}, need {input_schema['required_args']}")
                            input_valid = False
                    
                    if 'required_kwargs' in input_schema:
                        missing_kwargs = set(input_schema['required_kwargs']) - set(kwargs.keys())
                        if missing_kwargs:
                            validation_errors.append(f"Missing kwargs: {missing_kwargs}")
                            input_valid = False
                            
                except Exception as e:
                    validation_errors.append(f"Input validation error: {e}")
                    input_valid = False
            
            # Calculate data size
            data_size = len(str(args)) + len(str(kwargs))
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Validate output
            output_valid = True
            if output_schema:
                try:
                    if 'type' in output_schema:
                        expected_type = output_schema['type']
                        if not isinstance(result, expected_type):
                            validation_errors.append(f"Wrong output type: got {type(result)}, expected {expected_type}")
                            output_valid = False
                            
                    if 'not_none' in output_schema and output_schema['not_none']:
                        if result is None:
                            validation_errors.append("Output should not be None")
                            output_valid = False
                            
                except Exception as e:
                    validation_errors.append(f"Output validation error: {e}")
                    output_valid = False
            
            if not validation_errors:
                validation_errors = ["OK"]
            
            return result
            
        return wrapper
    return decorator


# ============================================================================
# CALL FLOW TRACING
# ============================================================================

def call_flow_tracer(depth: int = 3):
    """
    Trace function call flows and dependencies.
    
    Args:
        depth: Maximum call depth to trace
    
    Example:
        @fckprint.call_flow_tracer(depth=5)
        def complex_function():
            # Will trace nested function calls up to 5 levels deep
            pass
    """
    call_stack = []
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('call_depth', 'call_stack', 'caller_info', 'call_duration'))
        def wrapper(*args, **kwargs):
            # Get caller information
            frame = inspect.currentframe()
            caller_frame = frame.f_back
            caller_info = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"
            
            call_depth = len(call_stack)
            call_stack.append({
                'function': func.__name__,
                'start_time': time.time(),
                'caller': caller_info
            })
            
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                call_duration = time.time() - start_time
                
                return result
            finally:
                call_stack.pop()
                
        return wrapper
    return decorator


# ============================================================================
# DATABASE QUERY MONITORING
# ============================================================================

def db_monitor(slow_query_threshold: float = 0.5):
    """
    Monitor database queries and performance (simulated for demo).
    
    Args:
        slow_query_threshold: Time in seconds above which queries are considered slow
    
    Example:
        @fckprint.db_monitor(slow_query_threshold=1.0)
        def fetch_user_data(user_id):
            # Will track query performance and warn about slow queries
            pass
    """
    query_stats = {'total_queries': 0, 'slow_queries': 0, 'total_time': 0}
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('query_time', 'is_slow_query', 'query_stats', 'query_type'))
        def wrapper(*args, **kwargs):
            query_type = "SELECT"  # Simulated - could parse actual SQL
            if 'insert' in func.__name__.lower():
                query_type = "INSERT"
            elif 'update' in func.__name__.lower():
                query_type = "UPDATE"
            elif 'delete' in func.__name__.lower():
                query_type = "DELETE"
            
            start_time = time.time()
            result = func(*args, **kwargs)
            query_time = time.time() - start_time
            
            # Update stats
            query_stats['total_queries'] += 1
            query_stats['total_time'] += query_time
            
            is_slow_query = query_time > slow_query_threshold
            if is_slow_query:
                query_stats['slow_queries'] += 1
                print(f"🐌 Slow query detected in '{func.__name__}': {query_time:.3f}s")
            
            return result
            
        return wrapper
    return decorator


# ============================================================================
# API RATE LIMITING
# ============================================================================

def rate_limiter(max_calls: int = 10, time_window: int = 60):
    """
    Monitor and enforce API rate limiting.
    
    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
    
    Example:
        @fckprint.rate_limiter(max_calls=100, time_window=3600)
        def api_endpoint():
            # Will enforce maximum 100 calls per hour
            pass
    """
    call_history = []
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('calls_in_window', 'rate_limit_exceeded', 'time_until_reset'))
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Clean old calls outside time window
            call_history[:] = [t for t in call_history if current_time - t < time_window]
            
            calls_in_window = len(call_history)
            rate_limit_exceeded = calls_in_window >= max_calls
            
            if rate_limit_exceeded:
                oldest_call = min(call_history) if call_history else current_time
                time_until_reset = time_window - (current_time - oldest_call)
                raise Exception(f"Rate limit exceeded for '{func.__name__}'. Try again in {time_until_reset:.1f} seconds")
            
            # Add current call
            call_history.append(current_time)
            time_until_reset = 0
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# ============================================================================
# SECURITY MONITORING
# ============================================================================

def security_monitor(check_inputs: bool = True, mask_sensitive: bool = True):
    """
    Monitor for potential security issues in function inputs.
    
    Args:
        check_inputs: Whether to check inputs for security threats
        mask_sensitive: Whether to mask sensitive data in logs
    
    Example:
        @fckprint.security_monitor(check_inputs=True, mask_sensitive=True)
        def process_user_input(user_data, password=None):
            # Will check for SQL injection, XSS, and sensitive data
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('security_warnings', 'input_sanitized', 'sensitive_data_detected'))
        def wrapper(*args, **kwargs):
            security_warnings = []
            sensitive_data_detected = False
            input_sanitized = True
            
            if check_inputs:
                # Check for potential security issues
                all_inputs = str(args) + str(kwargs)
                
                # SQL injection patterns
                sql_patterns = ['DROP TABLE', 'DELETE FROM', '--', ';', 'UNION SELECT']
                for pattern in sql_patterns:
                    if pattern.lower() in all_inputs.lower():
                        security_warnings.append(f"POTENTIAL_SQL_INJECTION: {pattern}")
                        input_sanitized = False
                
                # XSS patterns
                xss_patterns = ['<script>', 'javascript:', 'onload=', 'onerror=']
                for pattern in xss_patterns:
                    if pattern.lower() in all_inputs.lower():
                        security_warnings.append(f"POTENTIAL_XSS: {pattern}")
                        input_sanitized = False
                
                # Sensitive data patterns
                sensitive_patterns = ['password', 'ssn', 'credit_card', 'api_key', 'secret']
                for pattern in sensitive_patterns:
                    if pattern.lower() in all_inputs.lower():
                        sensitive_data_detected = True
                        if mask_sensitive:
                            # Don't log the actual data
                            break
            
            if not security_warnings:
                security_warnings = ["OK"]
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# ============================================================================
# ADVANCED DECORATORS
# ============================================================================

def circuit_breaker(failure_threshold: int = 5, recovery_timeout: int = 60):
    """
    Implement circuit breaker pattern to prevent cascading failures.
    
    Args:
        failure_threshold: Number of failures before opening circuit
        recovery_timeout: Time in seconds before attempting to close circuit
    
    Example:
        @fckprint.circuit_breaker(failure_threshold=3, recovery_timeout=30)
        def external_api_call():
            # Will stop calling after 3 failures, retry after 30 seconds
            pass
    """
    failure_count = 0
    last_failure_time = 0
    circuit_open = False
    
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('circuit_open', 'failure_count', 'time_since_failure'))
        def wrapper(*args, **kwargs):
            nonlocal failure_count, last_failure_time, circuit_open
            
            current_time = time.time()
            time_since_failure = current_time - last_failure_time
            
            # Check if circuit should be closed (recovery attempt)
            if circuit_open and time_since_failure > recovery_timeout:
                circuit_open = False
                failure_count = 0
                print(f"🔄 Circuit breaker for '{func.__name__}' attempting recovery")
            
            if circuit_open:
                raise Exception(f"Circuit breaker OPEN for '{func.__name__}'. Try again in {recovery_timeout - time_since_failure:.1f} seconds")
            
            try:
                result = func(*args, **kwargs)
                # Success - reset failure count
                if failure_count > 0:
                    failure_count = 0
                    print(f"✅ Circuit breaker for '{func.__name__}' recovered")
                return result
            except Exception as e:
                failure_count += 1
                last_failure_time = current_time
                
                if failure_count >= failure_threshold:
                    circuit_open = True
                    print(f"🚨 Circuit breaker OPENED for '{func.__name__}' after {failure_count} failures")
                
                raise
                
        return wrapper
    return decorator


def feature_flag(flag_name: str, default_enabled: bool = True, environment_var: str = None):
    """
    Enable/disable function execution based on feature flags.
    
    Args:
        flag_name: Name of the feature flag
        default_enabled: Default state if flag is not set
        environment_var: Environment variable to check for flag state
    
    Example:
        @fckprint.feature_flag('NEW_ALGORITHM', default_enabled=False, environment_var='ENABLE_NEW_ALGO')
        def new_algorithm():
            # Will only execute if feature flag is enabled
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('flag_enabled', 'flag_source', 'flag_name'))
        def wrapper(*args, **kwargs):
            # Check environment variable first
            if environment_var and environment_var in os.environ:
                flag_enabled = os.environ[environment_var].lower() in ('true', '1', 'yes', 'on')
                flag_source = f"env:{environment_var}"
            else:
                flag_enabled = default_enabled
                flag_source = "default"
            
            if not flag_enabled:
                print(f"🚫 Feature '{flag_name}' is disabled, skipping '{func.__name__}'")
                return None
            
            print(f"✅ Feature '{flag_name}' is enabled, executing '{func.__name__}'")
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


def audit_trail(log_file: str = "fckprint_audit.log", include_args: bool = True):
    """
    Create an audit trail of function calls for compliance.
    
    Args:
        log_file: Path to audit log file
        include_args: Whether to include function arguments in audit log
    
    Example:
        @fckprint.audit_trail(log_file="user_actions.log", include_args=False)
        def delete_user(user_id):
            # All calls will be logged for audit purposes
            pass
    """
    def decorator(func):
        @functools.wraps(func)
        @snoop(watch=('audit_logged', 'user_context', 'action_type'))
        def wrapper(*args, **kwargs):
            timestamp = datetime.now().isoformat()
            user_context = getattr(threading.current_thread(), 'user_id', 'UNKNOWN')
            action_type = func.__name__
            
            audit_entry = {
                'timestamp': timestamp,
                'user': user_context,
                'action': action_type,
                'function': func.__name__,
                'module': func.__module__,
            }
            
            if include_args:
                audit_entry['args'] = str(args)[:200]  # Truncate for security
                audit_entry['kwargs'] = str(kwargs)[:200]
            
            try:
                with open(log_file, 'a') as f:
                    f.write(json.dumps(audit_entry) + '\n')
                audit_logged = True
            except Exception:
                audit_logged = False
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator


# ============================================================================
# DECORATOR COMBINATIONS
# ============================================================================

def production_monitor(
    performance_threshold: float = 2.0,
    max_retries: int = 1,
    cache_ttl: int = 300,
    rate_limit: int = 1000
):
    """
    Comprehensive production monitoring combining multiple decorators.
    
    Args:
        performance_threshold: Performance warning threshold in seconds
        max_retries: Number of retry attempts on failure
        cache_ttl: Cache time-to-live in seconds
        rate_limit: Maximum calls per hour
    
    Example:
        @fckprint.production_monitor(
            performance_threshold=1.0,
            max_retries=3,
            cache_ttl=600,
            rate_limit=500
        )
        def critical_api_endpoint():
            # Full production monitoring stack
            pass
    """
    def decorator(func):
        # Apply multiple decorators in order
        decorated_func = func
        decorated_func = performance_monitor(threshold=performance_threshold)(decorated_func)
        decorated_func = error_tracker(max_retries=max_retries)(decorated_func)
        decorated_func = cache_monitor(ttl=cache_ttl)(decorated_func)
        decorated_func = rate_limiter(max_calls=rate_limit, time_window=3600)(decorated_func)
        decorated_func = security_monitor()(decorated_func)
        
        return decorated_func
    return decorator


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'performance_monitor',
    'error_tracker', 
    'cache_monitor',
    'thread_monitor',
    'resource_monitor',
    'validate_data',
    'call_flow_tracer',
    'db_monitor',
    'rate_limiter',
    'security_monitor',
    'circuit_breaker',
    'feature_flag',
    'audit_trail',
    'production_monitor',
] 