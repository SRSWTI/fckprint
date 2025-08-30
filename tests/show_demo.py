"""
Demo of fckprint's show function - a better alternative to print
"""

from fckprint import show
import time

def traditional_print_demo():
    """Traditional print debugging"""
    print("=== traditional print debugging ===")
    
    x = 5
    y = 10
    result = x + y
    
    print("starting calculation")
    print(f"x = {x}")
    print(f"y = {y}")
    print(f"result = {result}")
    print("calculation complete")

def fckprint_show_demo():
    """fckprint show debugging"""
    print("=== fckprint show debugging ===")
    
    x = 5
    y = 10
    result = x + y
    
    show("starting calculation")
    show("x =", x)
    show("y =", y)
    show("result =", result)
    show("calculation complete")

def show_with_levels():
    """Demonstrate different log levels"""
    print("=== show with different levels ===")
    
    show("this is an info message")
    show("this is a debug message", level="debug")
    show("this is a warning message", level="warning")
    show("this is an error message", level="error")
    show("this is a success message", level="success")

def show_with_prefix():
    """Demonstrate prefix functionality"""
    print("=== show with prefixes ===")
    
    show("database query executed", prefix="DB", level="info")
    show("cache miss", prefix="CACHE", level="warning")
    show("user authenticated", prefix="AUTH", level="success")

def show_comparison():
    """Compare print vs show output"""
    print("=== print vs show comparison ===")
    
    print("traditional print output:")
    print("starting function")
    print("x = 5")
    print("y = 10")
    print("result = 15")
    print("finished function")
    
    print("\nfckprint show output:")
    show("starting function")
    show("x =", 5)
    show("y =", 10)
    show("result =", 15)
    show("finished function")



if __name__ == "__main__":
    traditional_print_demo()
    print()
    
    fckprint_show_demo()
    print()
    
    show_with_levels()
    print()
    
    show_with_prefix()
    print()
    
    show_comparison()
    print()
    
