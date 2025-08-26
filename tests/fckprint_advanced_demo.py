#!/usr/bin/env python3
"""
fckprint Advanced Decorators Demo

This comprehensive demo showcases all the advanced debugging decorators
available in fckprint v1.1.0, demonstrating how they can be used for
production monitoring, security, performance optimization, and more.

Copyright 2024 SRSWTI Research Labs
"""

import fckprint
import time
import random
import threading
import os
from datetime import datetime


def demo_separator(title: str):
    """Print a nice separator for demo sections"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


# ============================================================================
# PERFORMANCE MONITORING DEMOS
# ============================================================================

@fckprint.performance_monitor(threshold=0.1, memory_threshold=50)
def fast_computation():
    """Demo: Fast function that should pass performance checks"""
    return sum(range(1000))


@fckprint.performance_monitor(threshold=0.1, memory_threshold=10)
def slow_computation():
    """Demo: Slow function that will trigger performance warnings"""
    time.sleep(0.2)  # Intentionally slow
    data = [i**2 for i in range(10000)]  # Memory intensive
    return len(data)


@fckprint.resource_monitor(cpu_threshold=30.0, memory_threshold=60.0)
def resource_intensive_task():
    """Demo: Function that monitors system resource usage"""
    # Simulate CPU and memory intensive work
    result = sum(i**2 for i in range(50000))
    return result


# ============================================================================
# ERROR HANDLING & RELIABILITY DEMOS
# ============================================================================

@fckprint.error_tracker(log_file="demo_errors.log", max_retries=2)
def unreliable_network_call(fail_probability=0.7):
    """Demo: Simulated network call that might fail"""
    if random.random() < fail_probability:
        raise ConnectionError("Network timeout")
    return {"status": "success", "data": "important_data"}


@fckprint.circuit_breaker(failure_threshold=2, recovery_timeout=10)
def external_service_call(should_fail=False):
    """Demo: External service with circuit breaker protection"""
    if should_fail:
        raise RuntimeError("External service unavailable")
    return "Service response"


# ============================================================================
# CACHING & OPTIMIZATION DEMOS
# ============================================================================

@fckprint.cache_monitor(cache_size=5, ttl=10)
def expensive_calculation(n):
    """Demo: Expensive calculation with caching"""
    print(f"🔄 Computing fibonacci({n})...")
    time.sleep(0.1)  # Simulate expensive computation
    
    if n <= 1:
        return n
    return expensive_calculation(n-1) + expensive_calculation(n-2)


# ============================================================================
# CONCURRENCY & THREADING DEMOS
# ============================================================================

@fckprint.thread_monitor(max_concurrent=3)
def concurrent_database_operation(operation_id):
    """Demo: Database operation with concurrency monitoring"""
    print(f"🗄️  Executing DB operation {operation_id}")
    time.sleep(0.1)  # Simulate DB work
    return f"DB result for operation {operation_id}"


def threading_demo():
    """Demo: Multiple threads accessing the same function"""
    threads = []
    for i in range(5):
        thread = threading.Thread(
            target=concurrent_database_operation, 
            args=(i,)
        )
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()


# ============================================================================
# DATA VALIDATION & SECURITY DEMOS
# ============================================================================

@fckprint.validate_data(
    input_schema={'required_args': 2, 'required_kwargs': ['email']},
    output_schema={'type': dict, 'not_none': True}
)
def create_user_profile(name, age, email=None):
    """Demo: User profile creation with data validation"""
    if age < 0:
        return None  # This will trigger output validation error
    
    return {
        'name': name,
        'age': age,
        'email': email,
        'created_at': datetime.now().isoformat()
    }


@fckprint.security_monitor(check_inputs=True, mask_sensitive=True)
def process_user_data(user_input, password=None, credit_card=None):
    """Demo: Function with security monitoring"""
    # This will detect sensitive data in parameters
    processed = f"Processing: {user_input[:10]}..."
    return processed


@fckprint.security_monitor(check_inputs=True, mask_sensitive=False)
def vulnerable_function(sql_query):
    """Demo: Function that will trigger security warnings"""
    # This will detect potential SQL injection
    return f"Executing: {sql_query}"


# ============================================================================
# DEBUGGING & TRACING DEMOS
# ============================================================================

@fckprint.call_flow_tracer(depth=3)
def complex_calculation(n):
    """Demo: Complex calculation with call flow tracing"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return helper_function_a(n) + helper_function_b(n-1)


@fckprint.call_flow_tracer(depth=3)
def helper_function_a(x):
    """Helper function A"""
    return x * 2


@fckprint.call_flow_tracer(depth=3)
def helper_function_b(x):
    """Helper function B"""
    return nested_helper(x) + 1


@fckprint.call_flow_tracer(depth=3)
def nested_helper(x):
    """Deeply nested helper function"""
    return x // 2


# ============================================================================
# DATABASE & API DEMOS
# ============================================================================

@fckprint.db_monitor(slow_query_threshold=0.1)
def fetch_user_data(user_id):
    """Demo: Fast database query"""
    time.sleep(0.05)  # Fast query
    return {"user_id": user_id, "name": "Alice", "email": "alice@example.com"}


@fckprint.db_monitor(slow_query_threshold=0.1)
def complex_report_query():
    """Demo: Slow database query that will trigger warning"""
    time.sleep(0.2)  # Slow query
    return {"report": "monthly_sales", "rows": 50000}


@fckprint.rate_limiter(max_calls=3, time_window=5)
def api_endpoint(request_data):
    """Demo: Rate-limited API endpoint"""
    return {
        "status": "success",
        "data": request_data,
        "timestamp": time.time()
    }


# ============================================================================
# ADVANCED FEATURES DEMOS
# ============================================================================

@fckprint.feature_flag('NEW_ALGORITHM', default_enabled=True, environment_var='ENABLE_NEW_ALGO')
def new_sorting_algorithm(data):
    """Demo: Feature-flagged function"""
    print("🚀 Using new sorting algorithm!")
    return sorted(data, reverse=True)


@fckprint.feature_flag('EXPERIMENTAL_FEATURE', default_enabled=False)
def experimental_feature():
    """Demo: Disabled experimental feature"""
    print("🧪 This is an experimental feature!")
    return "experimental_result"


@fckprint.audit_trail(log_file="demo_audit.log", include_args=True)
def delete_user(user_id):
    """Demo: Audited function for compliance"""
    print(f"🗑️  Deleting user {user_id}")
    return f"User {user_id} deleted"


@fckprint.audit_trail(log_file="demo_audit.log", include_args=False)
def sensitive_operation():
    """Demo: Audited function without argument logging"""
    print("🔒 Performing sensitive operation")
    return "operation_completed"


# ============================================================================
# COMPOSITE DECORATORS DEMO
# ============================================================================

@fckprint.production_monitor(
    performance_threshold=0.5,
    max_retries=2,
    cache_ttl=30,
    rate_limit=10
)
def critical_business_function(operation_type, data):
    """Demo: Critical function with full production monitoring"""
    if operation_type == "slow":
        time.sleep(0.6)  # Will trigger performance warning
    elif operation_type == "fail":
        raise ValueError("Simulated business logic error")
    
    return {
        "operation": operation_type,
        "result": f"processed_{len(data)}_items",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# MAIN DEMO RUNNER
# ============================================================================

def run_comprehensive_demo():
    """Run the complete fckprint decorators demonstration"""
    
    print("🎭 fckprint v1.1.0 - Advanced Decorators Comprehensive Demo")
    print("🚀 Showcasing production-ready debugging and monitoring capabilities")
    
    # Performance Monitoring
    demo_separator("Performance Monitoring")
    print("✅ Fast function (should pass):")
    result = fast_computation()
    print(f"Result: {result}")
    
    print("\n⚠️  Slow function (should warn):")
    result = slow_computation()
    print(f"Result: {result}")
    
    print("\n📊 Resource monitoring:")
    result = resource_intensive_task()
    print(f"Result: {result}")
    
    # Error Handling
    demo_separator("Error Handling & Reliability")
    print("🔄 Testing unreliable function with retries:")
    try:
        result = unreliable_network_call(fail_probability=0.3)
        print(f"Success: {result}")
    except Exception as e:
        print(f"Failed: {e}")
    
    print("\n🔌 Testing circuit breaker:")
    try:
        # This should work
        result = external_service_call(should_fail=False)
        print(f"Success: {result}")
        
        # This will start failing and eventually open the circuit
        for i in range(3):
            try:
                external_service_call(should_fail=True)
            except Exception as e:
                print(f"Attempt {i+1} failed: {e}")
    except Exception as e:
        print(f"Circuit breaker: {e}")
    
    # Caching
    demo_separator("Caching & Optimization")
    print("🗄️  Testing cache with fibonacci:")
    print("First call (cache miss):")
    result = expensive_calculation(5)
    print(f"Result: {result}")
    
    print("\nSecond call (cache hit):")
    result = expensive_calculation(5)
    print(f"Result: {result}")
    
    # Threading
    demo_separator("Concurrency & Threading")
    print("🧵 Testing concurrent access:")
    threading_demo()
    
    # Data Validation
    demo_separator("Data Validation & Security")
    print("✅ Valid user creation:")
    user = create_user_profile("Alice", 30, email="alice@example.com")
    print(f"User created: {user}")
    
    print("\n❌ Invalid user creation (missing email):")
    try:
        user = create_user_profile("Bob", 25)  # Missing required email
    except Exception as e:
        print(f"Validation failed: {e}")
    
    print("\n🔒 Security monitoring (normal data):")
    result = process_user_data("normal user input", password="secret123")
    print(f"Result: {result}")
    
    print("\n⚠️  Security monitoring (suspicious data):")
    result = vulnerable_function("SELECT * FROM users; DROP TABLE users;")
    print(f"Result: {result}")
    
    # Call Flow Tracing
    demo_separator("Call Flow Tracing")
    print("🔍 Tracing complex function calls:")
    result = complex_calculation(3)
    print(f"Result: {result}")
    
    # Database & API
    demo_separator("Database & API Monitoring")
    print("⚡ Fast database query:")
    user = fetch_user_data(123)
    print(f"User: {user}")
    
    print("\n🐌 Slow database query:")
    report = complex_report_query()
    print(f"Report: {report}")
    
    print("\n🌐 API rate limiting test:")
    for i in range(4):  # This should hit rate limit on 4th call
        try:
            response = api_endpoint(f"request_{i}")
            print(f"API call {i+1}: {response['status']}")
        except Exception as e:
            print(f"API call {i+1} failed: {e}")
    
    # Advanced Features
    demo_separator("Advanced Features")
    print("🚩 Feature flags:")
    data = [3, 1, 4, 1, 5, 9, 2, 6]
    sorted_data = new_sorting_algorithm(data)
    print(f"Sorted: {sorted_data}")
    
    experimental_feature()  # Should be skipped
    
    print("\n📋 Audit trail:")
    delete_user(456)
    sensitive_operation()
    
    # Production Monitoring
    demo_separator("Production Monitoring (Composite)")
    print("🏭 Testing critical business function:")
    
    operations = [
        ("normal", "test_data"),
        ("slow", "slow_data"),  # Will trigger performance warning
    ]
    
    for op_type, data in operations:
        try:
            result = critical_business_function(op_type, data)
            print(f"Operation '{op_type}': {result}")
        except Exception as e:
            print(f"Operation '{op_type}' failed: {e}")
    
    demo_separator("Demo Complete! 🎉")
    print("📝 Check the following log files for detailed information:")
    print("   - demo_errors.log (error tracking)")
    print("   - demo_audit.log (audit trail)")
    print("   - fckprint_errors.log (default error log)")
    print("   - fckprint_audit.log (default audit log)")
    
    print("\n💡 Tips:")
    print("   - Combine decorators for comprehensive monitoring")
    print("   - Use environment variables to control feature flags")
    print("   - Adjust thresholds based on your application needs")
    print("   - Monitor log files for production insights")


if __name__ == "__main__":
    run_comprehensive_demo() 