import fckprint
import random

def foo():
    lst = []
    for i in range(10):
        lst.append(random.randrange(1, 1000))

    with fckprint.snoop():
        lower = min(lst)
        upper = max(lst)
        mid = (lower + upper) / 2
        print(lower, mid, upper)

@fckprint.snoop()
def number_to_bits(number):
    if number:
        bits = []
        while number:
            number, remainder = divmod(number, 2)
            bits.insert(0, remainder)
        return bits
    else:
        return [0]

if __name__ == "__main__":
    print("Testing fckprint ")
    print("\n=== Testing with context manager ===")
    foo()
    
    print("\n=== Testing with decorator ===")
    result = number_to_bits(6)
    print(f"Result: {result}") 