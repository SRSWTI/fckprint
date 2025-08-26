# Copyright 2025 SRSWTI Research Labs.

'''
fckprint - Never use print for debugging again!

An AI-enhanced debugger for Python, based on fckprint

Usage:

    import fckprint

    @fckprint.snoop()
    def your_function(x):
        ...

Advanced Usage with Decorators:

    @fckprint.performance_monitor(threshold=1.0)
    @fckprint.error_tracker(max_retries=3)
    @fckprint.cache_monitor(ttl=600)
    def production_function():
        ...

A log will be written to stderr showing the lines executed and variables
changed in the decorated function.

For more information, see https://github.com/SRSWTI/fckprint
Based on the original fckprint by Ram Rachum: https://github.com/cool-RR/fckprint
'''

from .tracer import Tracer as snoop
from .variables import Attrs, Exploding, Indices, Keys

# Import all decorators
from .decorators import (
    # Performance & Monitoring
    performance_monitor,
    resource_monitor,
    
    # Error Handling & Reliability  
    error_tracker,
    circuit_breaker,
    
    # Caching & Optimization
    cache_monitor,
    
    # Concurrency & Threading
    thread_monitor,
    
    # Data Validation & Security
    validate_data,
    security_monitor,
    
    # Debugging & Tracing
    call_flow_tracer,
    
    # Database & API
    db_monitor,
    rate_limiter,
    
    # Advanced Features
    feature_flag,
    audit_trail,
    
    # Composite Decorators
    production_monitor,
)

import collections

__VersionInfo = collections.namedtuple('VersionInfo',
                                       ('major', 'minor', 'micro'))

__version__ = '1.1.0'  # Bumped version for new decorators
__version_info__ = __VersionInfo(*(map(int, __version__.split('.'))))

# Make all decorators available at package level
__all__ = [
    # Core functionality
    'snoop',
    'Attrs', 
    'Exploding', 
    'Indices', 
    'Keys',
    
    # Performance & Monitoring
    'performance_monitor',
    'resource_monitor',
    
    # Error Handling & Reliability
    'error_tracker',
    'circuit_breaker',
    
    # Caching & Optimization  
    'cache_monitor',
    
    # Concurrency & Threading
    'thread_monitor',
    
    # Data Validation & Security
    'validate_data',
    'security_monitor',
    
    # Debugging & Tracing
    'call_flow_tracer',
    
    # Database & API
    'db_monitor',
    'rate_limiter',
    
    # Advanced Features
    'feature_flag',
    'audit_trail',
    
    # Composite Decorators
    'production_monitor',
]

del collections, __VersionInfo # Avoid polluting the namespace
