import fckprint
import time
import functools
import traceback
import psutil
import os
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import json
import threading
import inspect

# 1. Performance Monitoring Decorator
def performance_monitor(threshold: float = 1.0, memory_threshold: int = 100):
    """Monitor function performance and memory usage"""
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('execution_time', 'memory_usage', 'performance_warning'))
        def wrapper(*args, **kwargs):
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

# 2. Error Tracking Decorator
def error_tracker(log_file: str = "errors.log", max_retries: int = 0):
    """Track and log errors with optional retry logic"""
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('attempt', 'error_type', 'error_message', 'retry_success'))
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    retry_success = attempt > 0
                    if retry_success:
                        print(f"✅ Function succeeded on attempt {attempt + 1}")
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
                    
                    with open(log_file, 'a') as f:
                        f.write(json.dumps(error_log) + '\n')
                    
                    if attempt == max_retries:
                        retry_success = False
                        print(f"❌ Function failed after {max_retries + 1} attempts")
                        raise
                    else:
                        print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        
        return wrapper
    return decorator

# 3. Cache Monitor Decorator
def cache_monitor(cache_size: int = 100, ttl: int = 300):
    """Monitor function calls with caching"""
    cache = {}
    cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('cache_key', 'cache_hit', 'cache_stats', 'cache_size_current'))
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

# 4. Thread Safety Monitor
def thread_monitor(max_concurrent: int = 5):
    """Monitor thread usage and detect race conditions"""
    active_threads = {}
    lock = threading.Lock()
    
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('thread_id', 'active_count', 'concurrent_warning', 'thread_name'))
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

# 5. Resource Usage Monitor
def resource_monitor(cpu_threshold: float = 80.0, memory_threshold: float = 80.0):
    """Monitor CPU and memory usage during function execution"""
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('cpu_percent', 'memory_percent', 'resource_warning', 'disk_usage'))
        def wrapper(*args, **kwargs):
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

# 6. Data Validation Monitor
def validate_data(input_schema: Dict = None, output_schema: Dict = None):
    """Monitor and validate input/output data"""
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('input_valid', 'output_valid', 'validation_errors', 'data_size'))
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

# 7. Call Flow Tracer
def call_flow_tracer(depth: int = 3):
    """Trace function call flows and dependencies"""
    call_stack = []
    
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('call_depth', 'call_stack', 'caller_info', 'call_duration'))
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

# 8. Database Query Monitor (simulated)
def db_monitor(slow_query_threshold: float = 0.5):
    """Monitor database queries and performance"""
    query_stats = {'total_queries': 0, 'slow_queries': 0, 'total_time': 0}
    
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('query_time', 'is_slow_query', 'query_stats', 'query_type'))
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
                print(f"🐌 Slow query detected: {query_time:.3f}s")
            
            return result
            
        return wrapper
    return decorator

# 9. API Rate Limiter
def rate_limiter(max_calls: int = 10, time_window: int = 60):
    """Monitor and enforce API rate limiting"""
    call_history = []
    
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('calls_in_window', 'rate_limit_exceeded', 'time_until_reset'))
        def wrapper(*args, **kwargs):
            current_time = time.time()
            
            # Clean old calls outside time window
            call_history[:] = [t for t in call_history if current_time - t < time_window]
            
            calls_in_window = len(call_history)
            rate_limit_exceeded = calls_in_window >= max_calls
            
            if rate_limit_exceeded:
                oldest_call = min(call_history) if call_history else current_time
                time_until_reset = time_window - (current_time - oldest_call)
                raise Exception(f"Rate limit exceeded. Try again in {time_until_reset:.1f} seconds")
            
            # Add current call
            call_history.append(current_time)
            time_until_reset = 0
            
            return func(*args, **kwargs)
            
        return wrapper
    return decorator

# 10. Security Monitor
def security_monitor(check_inputs: bool = True, mask_sensitive: bool = True):
    """Monitor for potential security issues"""
    def decorator(func):
        @functools.wraps(func)
        @fckprint.snoop(watch=('security_warnings', 'input_sanitized', 'sensitive_data_detected'))
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

# Example usage and testing functions
@performance_monitor(threshold=0.1, memory_threshold=50)
def slow_function():
    """Example slow function"""
    time.sleep(0.2)  # Intentionally slow
    return "completed"

@error_tracker(max_retries=2)
def failing_function(should_fail: bool = True):
    """Example function that might fail"""
    if should_fail:
        raise ValueError("Simulated error")
    return "success"

@cache_monitor(cache_size=3, ttl=5)
def expensive_computation(x: int):
    """Example cached function"""
    time.sleep(0.1)  # Simulate expensive operation
    return x * x

@thread_monitor(max_concurrent=2)
def concurrent_function(task_id: int):
    """Example function for thread monitoring"""
    time.sleep(0.1)
    return f"Task {task_id} completed"

@resource_monitor(cpu_threshold=50.0, memory_threshold=50.0)
def resource_intensive_function():
    """Example resource-intensive function"""
    # Simulate some work
    data = [i for i in range(10000)]
    return len(data)

@validate_data(
    input_schema={'required_args': 1, 'required_kwargs': ['name']},
    output_schema={'type': str, 'not_none': True}
)
def data_processing_function(data, name=None):
    """Example function with data validation"""
    return f"Processed {data} for {name}"

@call_flow_tracer(depth=3)
def nested_function_a():
    """Example nested function A"""
    return nested_function_b()

@call_flow_tracer(depth=3)  
def nested_function_b():
    """Example nested function B"""
    return "nested result"

@db_monitor(slow_query_threshold=0.1)
def select_users():
    """Example database query function"""
    time.sleep(0.15)  # Simulate slow query
    return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

@rate_limiter(max_calls=3, time_window=10)
def api_endpoint():
    """Example rate-limited API endpoint"""
    return {"status": "success", "timestamp": time.time()}

@security_monitor(check_inputs=True, mask_sensitive=True)
def process_user_input(user_data: str, password: str = None):
    """Example function with security monitoring"""
    return f"Processed: {user_data}"

def run_custom_decorator_examples():
    """Run examples of all custom decorators"""
    print("🎭 Custom fckprint Decorators Demo")
    print("=" * 50)
    
    try:
        print("\n1️⃣ Performance Monitor:")
        result = slow_function()
        print(f"Result: {result}")
        
        print("\n2️⃣ Error Tracker:")
        try:
            failing_function(should_fail=False)
        except:
            pass
        
        print("\n3️⃣ Cache Monitor:")
        print(f"First call: {expensive_computation(5)}")
        print(f"Cached call: {expensive_computation(5)}")
        
        print("\n4️⃣ Thread Monitor:")
        result = concurrent_function(1)
        print(f"Thread result: {result}")
        
        print("\n5️⃣ Resource Monitor:")
        result = resource_intensive_function()
        print(f"Resource result: {result}")
        
        print("\n6️⃣ Data Validation:")
        result = data_processing_function("test_data", name="Alice")
        print(f"Validation result: {result}")
        
        print("\n7️⃣ Call Flow Tracer:")
        result = nested_function_a()
        print(f"Flow result: {result}")
        
        print("\n8️⃣ Database Monitor:")
        users = select_users()
        print(f"DB result: {len(users)} users")
        
        print("\n9️⃣ Rate Limiter:")
        for i in range(2):
            result = api_endpoint()
            print(f"API call {i+1}: {result['status']}")
        
        print("\n🔟 Security Monitor:")
        result = process_user_input("normal data", password="secret123")
        print(f"Security result: {result}")
        
        print("\n🎉 All custom decorators tested!")
        
    except Exception as e:
        print(f"❌ Error testing decorators: {e}")

if __name__ == "__main__":
    run_custom_decorator_examples() 