# fckprint

advanced debugging and monitoring for python applications

fckprint is a powerful debugging and monitoring library that provides comprehensive tracing, performance monitoring, error tracking, caching, and production-ready features for python applications.

## why fckprint over print?

traditional debugging with print statements is slow, messy, and doesn't scale. fckprint provides structured, detailed debugging that's faster and more informative.

### traditional print debugging (slow and messy)

```python
def calculate_fibonacci(n):
    print(f"entering calculate_fibonacci with n={n}")
    if n <= 1:
        print(f"base case: returning {n}")
        return n
    
    print(f"recursive case: calling calculate_fibonacci({n-1}) + calculate_fibonacci({n-2})")
    result = calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
    print(f"returning result: {result}")
    return result
```

output is messy and hard to follow:
```
entering calculate_fibonacci with n=5
recursive case: calling calculate_fibonacci(4) + calculate_fibonacci(3)
entering calculate_fibonacci with n=4
recursive case: calling calculate_fibonacci(3) + calculate_fibonacci(2)
entering calculate_fibonacci with n=3
recursive case: calling calculate_fibonacci(2) + calculate_fibonacci(1)
entering calculate_fibonacci with n=2
recursive case: calling calculate_fibonacci(1) + calculate_fibonacci(0)
entering calculate_fibonacci with n=1
base case: returning 1
entering calculate_fibonacci with n=0
base case: returning 0
returning result: 1
returning result: 1
returning result: 2
entering calculate_fibonacci with n=1
base case: returning 1
returning result: 3
returning result: 5
```

### fckprint debugging (fast and structured)

```python
import fckprint

@fckprint.snoop()
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
```

clean, structured output with timestamps and variable tracking:

```
17:21:32.924559 line        10         if n <= 1:
17:21:32.924657 line        11         return n
17:21:32.924677 line        12         return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
elapsed time: 00:00:00.000181
```

### fckprint show (print replacement)

```python
# direct import (recommended)
from fckprint import show

def calculate_fibonacci(n):
    show("entering fibonacci function with n =", n)
    if n <= 1:
        show("base case: returning", n)
        return n
    
    show("recursive case: calling fibonacci", n-1, "and", n-2)
    result = calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)
    show("returning result:", result)
    return result
```

structured output with timestamps and log levels:
```
[18:08:47.183] INFO entering fibonacci function with n = 5
[18:08:47.183] INFO recursive case: calling fibonacci 4 and 3
[18:08:47.183] INFO entering fibonacci function with n = 4
[18:08:47.183] INFO recursive case: calling fibonacci 3 and 2
[18:08:47.183] INFO entering fibonacci function with n = 3
[18:08:47.183] INFO recursive case: calling fibonacci 2 and 1
[18:08:47.183] INFO entering fibonacci function with n = 2
[18:08:47.183] INFO recursive case: calling fibonacci 1 and 0
[18:08:47.183] INFO entering fibonacci function with n = 1
[18:08:47.183] INFO base case: returning 1
[18:08:47.183] INFO entering fibonacci function with n = 2
[18:08:47.183] INFO base case: returning 0
[18:08:47.183] INFO returning result: 1
[18:08:47.183] INFO returning result: 1
[18:08:47.183] INFO returning result: 2
[18:08:47.183] INFO returning result: 3
[18:08:47.183] INFO returning result: 5
```

### why fckprint is better

1. **faster execution** - no manual print statements to slow down code
2. **structured output** - timestamps, line numbers, and variable tracking
3. **production ready** - can be disabled in production with environment variables
4. **comprehensive monitoring** - performance, errors, caching, security
5. **thread safe** - works correctly in multi-threaded applications
6. **configurable** - customize output format and verbosity
7. **non-intrusive** - minimal code changes required

## installation

```bash
uv pip install fckprint
```

or

```bash
pip install fckprint
```

## quick start

### basic function tracing:

```python
import fckprint

@fckprint.snoop()
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

result = fibonacci(5)
```

### print replacement with show:

```python
# direct import (recommended)
from fckprint import show

def fibonacci(n):
    show("calculating fibonacci for", n)
    if n <= 1:
        show("base case:", n)
        return n
    
    result = fibonacci(n - 1) + fibonacci(n - 2)
    show("result:", result)
    return result

# with log levels and prefixes:
show("starting calculation", level="info")
show("cache miss", level="warning", prefix="CACHE")
show("calculation complete", level="success")
```

## advanced debugging features

### custom variable watching

```python
@fckprint.snoop(watch=('x', 'y', 'result'))
def calculate(x, y):
    result = x * y + 10
    return result

calculate(5, 3)
```

### watch explosion for complex objects

```python
@fckprint.snoop(watch_explode=('user', 'config'))
def process_user(user, config):
    # automatically expand all attributes of user and config objects
    return user.name + config.environment
```

### thread information

```python
@fckprint.snoop(thread_info=True)
def threaded_function():
    return "executed in thread"
```

### custom prefixes for easy grepping

```python
@fckprint.snoop(prefix='debug: ')
def debug_function():
    return "debug output"
```

## production monitoring decorators

fckprint provides powerful decorators that help you monitor, debug, and optimize your production applications. Each decorator automatically tracks relevant metrics and provides structured output to help you understand what's happening in your code.

### performance monitoring

**What it does:** Monitors function execution time and memory usage to identify performance bottlenecks.

**How it helps:**
- Automatically detects slow functions that exceed your threshold
- Tracks memory consumption to prevent memory leaks
- Provides structured warnings when performance degrades
- Works with or without psutil (gracefully degrades)

```python
@fckprint.performance_monitor(threshold=0.5, memory_threshold=100)
def expensive_function():
    # function will be monitored for performance issues
    time.sleep(0.2)
    return "result"

result = expensive_function()
```

output:
```
starting var:.. execution_time = 0
starting var:.. memory_usage = 0
starting var:.. performance_warning = ['psutil_not_available']
new var:....... result = result
modified var:.. execution_time = 0.2091982364654541
modified var:.. performance_warning = ['slow: 0.21s > 0.1s']
return value:.. result
elapsed time: 00:00:00.209508
```

### error tracking and retry logic

**What it does:** Automatically retries failed functions with exponential backoff and logs all errors for analysis.

**How it helps:**
- Prevents transient failures from breaking your application
- Provides detailed error logs with timestamps and context
- Implements smart retry strategies with exponential backoff
- Helps identify patterns in failures for debugging

```python
@fckprint.error_tracker(max_retries=3, log_file="api_errors.log")
def unreliable_network_call(fail_probability=0.3):
    if random.random() < fail_probability:
        raise ConnectionError("network timeout")
    return {"status": "success", "data": "important_data"}

result = unreliable_network_call()
```

output:
```
starting var:.. attempt = 0
new var:....... result = {'status': 'success', 'data': 'important_data'}
new var:....... retry_success = false
return value:.. {'status': 'success', 'data': 'important_data'}
elapsed time: 00:00:00.000285
```

### caching and optimization

**What it does:** Implements intelligent caching with TTL and size limits to improve performance.

**How it helps:**
- Reduces redundant expensive computations
- Provides cache hit/miss statistics for optimization
- Automatically manages cache size and expiration
- Helps identify which functions benefit most from caching

```python
@fckprint.cache_monitor(cache_size=50, ttl=600)
def expensive_calculation(x, y):
    # results will be cached for 10 minutes
    time.sleep(0.1)
    return x * y

# first call (cache miss)
result1 = expensive_calculation(5, 10)
# second call (cache hit)
result2 = expensive_calculation(5, 10)
```

output:
```
starting var:.. cache_hit = false
starting var:.. cache_stats = {'hits': 0, 'misses': 1, 'evictions': 0}
new var:....... result = 50
elapsed time: 00:00:00.640305

starting var:.. cache_hit = true
starting var:.. cache_stats = {'hits': 1, 'misses': 1, 'evictions': 0}
return value:.. 50
elapsed time: 00:00:00.000545
```

### thread safety monitoring

**What it does:** Detects potential race conditions and high concurrency issues in multi-threaded applications.

**How it helps:**
- Identifies when too many threads are accessing the same function
- Warns about potential race conditions before they cause bugs
- Provides visibility into thread usage patterns
- Helps optimize thread pool sizes and concurrency limits

```python
@fckprint.thread_monitor(max_concurrent=3)
def database_operation(operation_id):
    time.sleep(0.1)
    return f"db result for operation {operation_id}"

# simulate concurrent access
import threading
threads = []
for i in range(5):
    thread = threading.Thread(target=database_operation, args=(i,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
```

output:
```
starting var:.. concurrent_warning = ['high_concurrency: 4 > 3', 'race_condition_risk: 4 instances']
new var:....... result = 'db result for operation 0'
elapsed time: 00:00:00.107264
```

### data validation

**What it does:** Validates input and output data against schemas to catch errors early.

**How it helps:**
- Catches data type errors and missing required fields
- Ensures function contracts are met
- Provides clear error messages for debugging
- Helps maintain data integrity across your application

```python
@fckprint.validate_data(
    input_schema={'required_args': 2, 'required_kwargs': ['email']},
    output_schema={'type': dict, 'not_none': True}
)
def create_user_profile(name, age, email=None):
    return {'name': name, 'age': age, 'email': email, 'created_at': datetime.now().isoformat()}

# valid call
user1 = create_user_profile('alice', 30, email='alice@example.com')

# invalid call (missing email)
user2 = create_user_profile('bob', 25)
```

output:
```
starting var:.. validation_errors = ['ok']
new var:....... result = {'name': 'alice', 'age': 30, 'email': 'alice@example.com', 'created_at': '2025-08-26t17:21:48.507150'}
elapsed time: 00:00:00.001011

starting var:.. validation_errors = ["missing kwargs: {'email'}"]
new var:....... result = {'name': 'bob', 'age': 25, 'email': None, 'created_at': '2025-08-26t17:21:48.508061'}
elapsed time: 00:00:00.000828
```

### security monitoring

**What it does:** Detects potential security threats in function inputs and masks sensitive data.

**How it helps:**
- Identifies potential SQL injection and XSS attacks
- Automatically masks sensitive data in logs
- Provides security warnings for suspicious input patterns
- Helps maintain security compliance in production

```python
@fckprint.security_monitor(check_inputs=True, mask_sensitive=True)
def process_user_data(user_input, password=None):
    return f"processing: {user_input}"

# normal data
result1 = process_user_data("normal user input", password="secret123")

# suspicious data
result2 = process_user_data("select * from users; drop table users;")
```

output:
```
starting var:.. security_warnings = ['ok']
starting var:.. sensitive_data_detected = true
return value:.. 'processing: normal user input'
elapsed time: 00:00:00.002813

starting var:.. security_warnings = ['potential_sql_injection: drop table', 'potential_sql_injection: ;']
starting var:.. input_sanitized = false
return value:.. 'executing: select * from users; drop table users;'
elapsed time: 00:00:00.001514
```

### circuit breaker pattern

**What it does:** Prevents cascading failures in distributed systems by temporarily stopping calls to failing services.

**How it helps:**
- Prevents one failing service from bringing down your entire system
- Automatically recovers when services become healthy again
- Provides clear feedback about service availability
- Implements industry-standard circuit breaker patterns

```python
@fckprint.circuit_breaker(failure_threshold=2, recovery_timeout=10)
def external_service_call(should_fail=False):
    if should_fail:
        raise RuntimeError("external service unavailable")
    return "service response"

# successful calls
result1 = external_service_call(should_fail=False)

# failing calls that trigger circuit breaker
try:
    result2 = external_service_call(should_fail=True)
except Exception as e:
    print(f"attempt 1 failed: {e}")

try:
    result3 = external_service_call(should_fail=True)
except Exception as e:
    print(f"attempt 2 failed: {e}")

# circuit breaker opens
try:
    result4 = external_service_call(should_fail=True)
except Exception as e:
    print(f"attempt 3 failed: {e}")
```

output:
```
starting var:.. circuit_open = false
starting var:.. failure_count = 0
return value:.. 'service response'
elapsed time: 00:00:00.000319

starting var:.. failure_count = 1
starting var:.. last_failure_time = 1756243307.7477162
call ended by exception
elapsed time: 00:00:00.000466

starting var:.. failure_count = 2
starting var:.. circuit_open = true
circuit breaker opened for 'external_service_call' after 2 failures
call ended by exception
elapsed time: 00:00:00.000451

starting var:.. circuit_open = true
call ended by exception
elapsed time: 00:00:00.000238
```

### feature flags

**What it does:** Enables/disables functions based on environment variables for safe feature rollouts.

**How it helps:**
- Safely deploy new features without affecting all users
- A/B test different implementations
- Quickly disable problematic features in production
- Implement gradual rollouts and canary deployments

```python
@fckprint.feature_flag('new_algorithm', default_enabled=True, environment_var='enable_new_algo')
def new_sorting_algorithm(data):
    print("using new sorting algorithm!")
    return sorted(data, reverse=True)

@fckprint.feature_flag('experimental_feature', default_enabled=False)
def experimental_feature():
    return "experimental result"

# enabled feature
result1 = new_sorting_algorithm([3, 1, 4, 1, 5, 9, 2, 6])

# disabled feature
result2 = experimental_feature()
```

output:
```
feature 'new_algorithm' is enabled, executing 'new_sorting_algorithm'
using new sorting algorithm!
return value:.. [9, 6, 5, 4, 3, 2, 1, 1]
elapsed time: 00:00:00.000253

feature 'experimental_feature' is disabled, skipping 'experimental_feature'
return value:.. None
elapsed time: 00:00:00.000210
```

### audit trail

**What it does:** Creates compliance audit logs for sensitive operations and user actions.

**How it helps:**
- Maintains compliance with security and privacy regulations
- Provides complete audit trail for debugging and forensics
- Tracks user actions for accountability
- Helps with security incident response and investigation

```python
@fckprint.audit_trail(log_file="user_actions.log", include_args=True)
def delete_user(user_id):
    print(f"deleting user {user_id}")
    return f"user {user_id} deleted"

@fckprint.audit_trail(log_file="user_actions.log", include_args=False)
def sensitive_operation():
    print("performing sensitive operation")
    return "operation_completed"

result1 = delete_user(456)
result2 = sensitive_operation()
```

output:
```
starting var:.. audit_logged = true
deleting user 456
return value:.. 'user 456 deleted'
elapsed time: 00:00:00.000902

starting var:.. audit_logged = true
performing sensitive operation
return value:.. 'operation_completed'
elapsed time: 00:00:00.000546
```

### rate limiting

**What it does:** Enforces API rate limits to prevent abuse and ensure fair resource usage.

**How it helps:**
- Prevents API abuse and DoS attacks
- Ensures fair resource distribution among users
- Provides clear feedback when limits are exceeded
- Helps maintain system stability under high load

```python
@fckprint.rate_limiter(max_calls=10, time_window=60)
def api_endpoint():
    return "api response"

# simulate rapid calls
for i in range(15):
    try:
        result = api_endpoint()
        print(f"call {i+1}: success")
    except Exception as e:
        print(f"call {i+1}: {e}")
```

### resource monitoring

**What it does:** Monitors system CPU, memory, and disk usage during function execution.

**How it helps:**
- Identifies resource bottlenecks before they cause problems
- Provides early warning of system stress
- Helps optimize resource allocation
- Monitors system health in production environments

```python
@fckprint.resource_monitor(cpu_threshold=80.0, memory_threshold=80.0)
def resource_intensive_task():
    # will warn if system resources are under stress
    time.sleep(0.1)
    return "task completed"

result = resource_intensive_task()
```

### production monitoring

**What it does:** Combines multiple monitoring decorators for comprehensive production oversight.

**How it helps:**
- Provides complete visibility into production function behavior
- Combines performance, error handling, caching, and security monitoring
- Reduces the need to manually combine multiple decorators
- Ensures consistent monitoring across critical functions

```python
@fckprint.production_monitor(
    performance_threshold=1.0,
    max_retries=3,
    cache_ttl=600,
    rate_limit=500
)
def critical_api_endpoint(operation_type, data):
    if operation_type == "slow":
        time.sleep(0.6)
    return {
        'operation': operation_type,
        'result': 'processed_9_items',
        'timestamp': datetime.now().isoformat()
    }

result1 = critical_api_endpoint('normal', 'test_data')
result2 = critical_api_endpoint('slow', 'slow_data')
```

output:
```
starting var:.. security_warnings = ['ok']
starting var:.. cache_hit = false
starting var:.. performance_warning = ['ok']
return value:.. {'operation': 'normal', 'result': 'processed_9_items', 'timestamp': '2025-08-26t17:21:48.780563'}
elapsed time: 00:00:00.004234

starting var:.. performance_warning = ['slow: 0.60s > 0.5s']
return value:.. {'operation': 'slow', 'result': 'processed_9_items', 'timestamp': '2025-08-26t17:21:49.388684'}
elapsed time: 00:00:00.608647
```

## configuration

### environment variables

```bash
# disable fckprint completely
export fckprint_DISABLED=1

# set custom log file
export fckprint_log_file=my_app.log

# enable debug mode
export fckprint_debug=1
```

### global settings

```python
import fckprint

# set global configuration
fckprint.set_config(
    max_variable_length=200,
    color=False,
    normalize=True,
    relative_time=True
)
```

## log files

fckprint creates several log files for different purposes:

- `fckprint_errors.log` - error tracking and retry attempts
- `fckprint_audit.log` - audit trail for compliance
- `demo_errors.log` - custom error logs
- `demo_audit.log` - custom audit logs

## tips for production use

1. **combine decorators** for comprehensive monitoring
2. **use environment variables** to control feature flags
3. **adjust thresholds** based on your application needs
4. **monitor log files** for production insights
5. **use caching** for expensive operations
6. **implement circuit breakers** for external services
7. **validate data** at function boundaries
8. **audit sensitive operations** for compliance

## examples

see the `tests/` directory for comprehensive examples:

- `fckprint_advanced_demo.py` - complete demonstration of all features
- `fckprint_custom_decorators.py` - custom decorator examples
- `ml_advanced_examples.py` - machine learning monitoring examples
- `api_debugging_examples.py` - api debugging patterns

## license

mit license - see license file for details

## contributing

contributions are welcome! please read the contributing guidelines and submit pull requests.

## support

for support and questions:
- open an issue on github
- check the documentation
- review the examples in the tests directory