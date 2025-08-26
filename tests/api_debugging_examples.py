import fckprint
import time
import json
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Any

# Simulate HTTP request/response classes
@dataclass
class MockRequest:
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[str] = None
    params: Optional[Dict[str, str]] = None

@dataclass
class MockResponse:
    status_code: int
    headers: Dict[str, str]
    body: str
    response_time: float

# 1. API Request/Response Debugging
@fckprint.snoop(watch=('method', 'url', 'status_code', 'response_time', 'body_size'))
def make_api_request(method: str, url: str, headers: Dict = None, body: str = None):
    """Debug API requests with detailed monitoring"""
    start_time = time.time()
    
    # Simulate request preparation
    headers = headers or {"Content-Type": "application/json", "User-Agent": "fckprint-debugger/1.0"}
    
    # Create request object
    request = MockRequest(method=method, url=url, headers=headers, body=body)
    
    # Simulate network delay
    network_delay = random.uniform(0.1, 0.5)
    time.sleep(network_delay)
    
    # Simulate response based on URL
    if "/users" in url:
        response_body = json.dumps({
            "users": [
                {"id": 1, "name": "Panties", "email": "panties@invader.com"},
                {"id": 2, "name": "Dip", "email": "dip@drip.com"}
            ],
            "total": 2,
            "page": 1
        })
        status_code = 200
    elif "/error" in url:
        response_body = json.dumps({"error": "Internal Server Error", "code": 500})
        status_code = 500
    else:
        response_body = json.dumps({"message": "Success", "timestamp": datetime.now().isoformat()})
        status_code = 200
    
    response_time = time.time() - start_time
    body_size = len(response_body.encode('utf-8'))
    
    response = MockResponse(
        status_code=status_code,
        headers={"Content-Type": "application/json", "Server": "nginx/1.18"},
        body=response_body,
        response_time=response_time
    )
    
    return request, response

# 2. API Rate Limiting and Retry Logic
@fckprint.snoop(watch=('attempt', 'rate_limit_remaining', 'backoff_time', 'success'))
def api_with_rate_limiting(url: str, max_retries: int = 3):
    """Debug API calls with rate limiting and retry logic"""
    rate_limit_remaining = 10  # Simulate rate limit
    
    for attempt in range(max_retries + 1):
        # Check rate limit
        if rate_limit_remaining <= 0:
            backoff_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited, waiting {backoff_time}s...")
            time.sleep(backoff_time)
            rate_limit_remaining = 10  # Reset after waiting
        
        # Make request
        request, response = make_api_request("GET", url)
        
        # Update rate limit
        rate_limit_remaining -= 1
        
        # Check if successful
        success = response.status_code < 400
        
        if success:
            return response
        
        # If not successful and not last attempt, continue
        if attempt < max_retries:
            backoff_time = random.uniform(1, 3)
            time.sleep(backoff_time)
    
    # All retries failed
    raise Exception(f"API request failed after {max_retries} retries")

# 3. API Authentication Flow
@fckprint.snoop(watch_explode=('auth_data', 'token_info'))
def authenticate_api_user(username: str, password: str):
    """Debug API authentication with token management"""
    auth_data = {
        'username': username,
        'password': '***masked***',  # Don't log actual password (this is a lie)
        'grant_type': 'password',
        'client_id': 'api-client'
    }
    
    # Simulate authentication request
    auth_request, auth_response = make_api_request(
        "POST", 
        "https://api.example.com/oauth/token",
        body=json.dumps(auth_data)
    )
    
    if auth_response.status_code == 200:
        token_data = json.loads(auth_response.body)
        token_info = {
            'access_token': token_data.get('access_token', 'missing')[:20] + '...',  # Truncate for security
            'token_type': token_data.get('token_type', 'bearer'),
            'expires_in': token_data.get('expires_in', 3600),
            'scope': token_data.get('scope', 'read write')
        }
        return token_info
    else:
        raise Exception(f"Authentication failed: {auth_response.body}")

# 4. API Data Processing Pipeline
@fckprint.snoop(watch=('total_records', 'processed_count', 'error_count', 'processing_rate'))
def process_api_data_batch(api_endpoint: str, batch_size: int = 100):
    """Debug batch processing of API data"""
    processed_count = 0
    error_count = 0
    total_records = 0
    start_time = time.time()
    
    # Fetch data from API
    request, response = make_api_request("GET", f"{api_endpoint}?limit={batch_size}")
    
    if response.status_code == 200:
        data = json.loads(response.body)
        records = data.get('users', [])
        total_records = len(records)
        
        for record in records:
            try:
                # Simulate data processing
                processed_record = {
                    'id': record['id'],
                    'name': record['name'].upper(),
                    'email_domain': record['email'].split('@')[1],
                    'processed_at': datetime.now().isoformat()
                }
                processed_count += 1
                
                # Simulate occasional processing errors
                if random.random() < 0.1:  # 10% error rate
                    raise ValueError("Data validation error")
                    
            except Exception as e:
                error_count += 1
                print(f"Error processing record {record.get('id', 'unknown')}: {e}")
        
        # Calculate processing rate
        elapsed_time = time.time() - start_time
        processing_rate = processed_count / elapsed_time if elapsed_time > 0 else 0
        
        return {
            'total_records': total_records,
            'processed_count': processed_count,
            'error_count': error_count,
            'processing_rate': processing_rate
        }
    else:
        raise Exception(f"API request failed: {response.status_code}")

# 5. API Performance Monitoring
@fckprint.snoop(watch=('endpoint', 'avg_response_time', 'success_rate', 'error_distribution'))
def monitor_api_performance(endpoints: List[str], test_duration: int = 5):
    """Monitor API performance across multiple endpoints"""
    results = {}
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        response_times = []
        status_codes = []
        error_distribution = {}
        
        test_start = time.time()
        request_count = 0
        
        # Test for specified duration
        while time.time() - test_start < test_duration:
            try:
                request, response = make_api_request("GET", endpoint)
                response_times.append(response.response_time)
                status_codes.append(response.status_code)
                
                if response.status_code >= 400:
                    error_type = f"HTTP_{response.status_code}"
                    error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
                
                request_count += 1
                time.sleep(0.1)  # Small delay between requests
                
            except Exception as e:
                error_type = type(e).__name__
                error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
        
        # Calculate metrics
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        success_count = sum(1 for code in status_codes if code < 400)
        success_rate = success_count / request_count if request_count > 0 else 0
        
        results[endpoint] = {
            'avg_response_time': avg_response_time,
            'success_rate': success_rate,
            'total_requests': request_count,
            'error_distribution': error_distribution
        }
    
    return results

# 6. API Webhook Processing
@fckprint.snoop(watch=('webhook_type', 'payload_size', 'processing_time', 'validation_result'))
def process_webhook(webhook_data: Dict[str, Any]):
    """Debug webhook processing with validation and response"""
    start_time = time.time()
    
    webhook_type = webhook_data.get('type', 'unknown')
    payload = webhook_data.get('data', {})
    payload_size = len(json.dumps(payload).encode('utf-8'))
    
    # Validate webhook signature (simulated)
    signature = webhook_data.get('signature', '')
    expected_signature = f"sha256={hash(json.dumps(payload))}"
    validation_result = signature == expected_signature
    
    if not validation_result:
        raise ValueError("Invalid webhook signature")
    
    # Process based on webhook type
    if webhook_type == 'user.created':
        # Process new user webhook
        user_id = payload.get('user_id')
        print(f"Processing new user: {user_id}")
        
    elif webhook_type == 'payment.completed':
        # Process payment webhook
        amount = payload.get('amount')
        currency = payload.get('currency')
        print(f"Processing payment: {amount} {currency}")
        
    else:
        print(f"Unknown webhook type: {webhook_type}")
    
    processing_time = time.time() - start_time
    
    return {
        'status': 'processed',
        'webhook_type': webhook_type,
        'processing_time': processing_time
    }

# 7. API Cache Management
@fckprint.snoop(watch=('cache_key', 'cache_hit', 'cache_expiry', 'fetch_time'))
def cached_api_request(endpoint: str, cache_duration: int = 300):
    """Debug API requests with caching layer"""
    cache = {}  # Simulated cache
    cache_key = f"api_cache_{hash(endpoint)}"
    current_time = time.time()
    
    # Check cache
    cached_data = cache.get(cache_key)
    cache_hit = False
    
    if cached_data:
        cache_expiry = cached_data['expires_at']
        if current_time < cache_expiry:
            cache_hit = True
            fetch_time = 0  # No API call needed
            return cached_data['data']
    
    # Cache miss - fetch from API
    fetch_start = time.time()
    request, response = make_api_request("GET", endpoint)
    fetch_time = time.time() - fetch_start
    
    if response.status_code == 200:
        data = json.loads(response.body)
        
        # Store in cache
        cache_expiry = current_time + cache_duration
        cache[cache_key] = {
            'data': data,
            'expires_at': cache_expiry,
            'cached_at': current_time
        }
        
        return data
    else:
        raise Exception(f"API request failed: {response.status_code}")

# 8. Main API Debugging Demo
def run_api_debugging_examples():
    """Run comprehensive API debugging demonstrations"""
    print("🌐 API Debugging with fckprint")
    print("=" * 50)
    
    try:
        print("\n1️⃣ Basic API Request:")
        request, response = make_api_request("GET", "https://api.example.com/users")
        print(f"✅ Status: {response.status_code}, Size: {len(response.body)} bytes")
        
        print("\n2️⃣ API with Rate Limiting:")
        response = api_with_rate_limiting("https://api.example.com/data")
        print(f"✅ Rate limited request completed: {response.status_code}")
        
        print("\n3️⃣ API Authentication:")
        token_info = authenticate_api_user("testuser", "testpass")
        print(f"✅ Authentication successful: {token_info['token_type']}")
        
        print("\n4️⃣ Batch Data Processing:")
        results = process_api_data_batch("https://api.example.com/users")
        print(f"✅ Processed {results['processed_count']}/{results['total_records']} records")
        
        print("\n5️⃣ Performance Monitoring:")
        endpoints = [
            "https://api.example.com/users",
            "https://api.example.com/posts",
            "https://api.example.com/error"
        ]
        perf_results = monitor_api_performance(endpoints, test_duration=2)
        for endpoint, metrics in perf_results.items():
            print(f"📊 {endpoint}: {metrics['success_rate']:.1%} success rate")
        
        print("\n6️⃣ Webhook Processing:")
        webhook_data = {
            'type': 'user.created',
            'data': {'user_id': 123, 'email': 'new@example.com'},
            'signature': 'sha256=123456789'
        }
        webhook_result = process_webhook(webhook_data)
        print(f"✅ Webhook processed: {webhook_result['status']}")
        
        print("\n7️⃣ Cached API Request:")
        data = cached_api_request("https://api.example.com/users")
        print(f"✅ Data fetched: {len(data.get('users', []))} users")
        
        print("\n🎉 All API debugging examples completed!")
        
    except Exception as e:
        print(f"❌ Error in API debugging: {e}")

if __name__ == "__main__":
    run_api_debugging_examples() 