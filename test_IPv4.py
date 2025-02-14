from ctypes import CDLL
import ctypes
import pytest

ipv4 = CDLL("./IPv4.so")

#int add(unsigned int base, char mask) 
ipv4.add.argtypes = [ctypes.c_uint, ctypes.c_char] #uint, char
ipv4.add.restype = ctypes.c_int  # return type: int

#int del(unsigned int base, char mask) 
#cant use "del" as a attribute name since it's pythons's built in keyword
ipv4.del_prefix = getattr(ipv4, "del")  # therefor rename to avoid conflict
ipv4.del_prefix.argtypes = [ctypes.c_uint, ctypes.c_char] #uint, char 
ipv4.del_prefix.restype = ctypes.c_int  # return type: int

#char check(unsigned int ip)
ipv4.check.argtypes = [ctypes.c_uint] #uint
ipv4.check.restype = ctypes.c_char  # return type: char


#helper function - ip converter
def ip_to_int(ip_str):
    parts = list(map(int, ip_str.split(".")))  # split string by dot into 4
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

#fixtures
@pytest.fixture
def empty_ipv4():
    for base in range(64):  # Try clearing possible entries
        for mask in range(33):
            ipv4.del_prefix(base, mask)
    return ipv4

@pytest.fixture
def ipv4_with_example():
    base = ip_to_int("10.20.0.0")
    mask = 16
    ipv4.add(base, mask)
    return ipv4, base, mask  # Return the test values

#add test cases
def test_add_single_prefix_valid(empty_ipv4):
    base = ip_to_int("10.20.0.0")
    mask = 16
    result = empty_ipv4.add(base,mask)
    assert result == 0, f"add(base,mask) function valid test failed - function returned {result}"

def test_add_prefix_with_smallest_mask_valid(): # /32
    pass

def test_add_prefix_with_largest_mask_valid(): # /0
    pass

def test_add_multiple_valid_prefixes_valid():
    pass

def test_add_base_greater_than_255_invalid():
    pass

def test_add_prefix_with_negative_base_invalid():
    pass

def test_add_already_existing_prefix_invalid():
    pass

def test_add_mask_outside_of_range_invalid(empty_ipv4):
    base = ip_to_int("10.20.0.0")
    mask = 33  #invalid mask (valid range: 0-32)
    result = empty_ipv4.add(base,mask)
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

#del test cases
def test_del_existing_prefix_valid():
    pass

def test_del_existing_smallest_mask_prefix_valid(): # /32
    pass

def test_del_existing_largest_mask_prefix_valid(): # /0
    pass

def test_del_nonexisting_prefix_invalid():
    pass

def test_del_prefix_with_out_of_range_base_invalid():
    pass

def test_del_prefix_with_out_of_range_mask_invalid():
    pass

def test_del_prefix_with_negative_base_invalid():
    pass



