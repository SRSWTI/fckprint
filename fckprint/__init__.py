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

# Define show function at module level for direct import
def show(*args, **kwargs):
    """
    fckprint's print equivalent - structured output with timestamps and context.
    
    Args:
        *args: Values to display
        **kwargs: Optional formatting options
        
    Examples:
        show("hello world")                    # Basic output
        show("x =", x, "y =", y)              # Multiple values
        show("debug info", level="info")       # With metadata
        show("error occurred", level="error")  # Error level
    """
    import sys
    import time
    from datetime import datetime
    
    # Get current timestamp
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    # Get caller information
    import inspect
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    caller_info = f"{caller_frame.f_code.co_filename}:{caller_frame.f_lineno}"
    
    # Format the output
    level = kwargs.get('level', 'info')
    prefix = kwargs.get('prefix', '')
    
    # Color coding based on level
    colors = {
        'info': '\033[36m',    # Cyan
        'debug': '\033[34m',   # Blue  
        'warning': '\033[33m', # Yellow
        'error': '\033[31m',   # Red
        'success': '\033[32m', # Green
    }
    
    color = colors.get(level, colors['info'])
    reset = '\033[0m'
    
    # Build the message
    message = ' '.join(str(arg) for arg in args)
    
    # Format the output line
    output = f"{color}[{timestamp}] {level.upper()}{reset} {message}"
    
    if prefix:
        output = f"{color}[{prefix}] {output}"
    
    # Add caller info in debug mode
    if level == 'debug':
        output += f" {color}({caller_info}){reset}"
    
    # Write to stderr (like fckprint)
    print(output, file=sys.stderr)
    
    return output

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
    'show',
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
