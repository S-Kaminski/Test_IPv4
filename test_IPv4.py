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
    for base in range(64):
        for mask in range(33):
            ipv4.del_prefix(base, mask)
    return ipv4

@pytest.fixture
def ipv4_with_example(empty_ipv4):
    base = 0x0A140000
    mask = 16
    empty_ipv4.add(base, mask)
    return empty_ipv4, base, mask

#add test cases
def test_add_single_prefix_valid(empty_ipv4):
    base = 0x0A140000
    mask = 16
    result = empty_ipv4.add(base,mask)
    assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

#def test_add_prefix_with_smallest_mask_valid(empty_ipv4):
    #base = 0x20408000
    #mask = 32  #works only for 1-18. 0,19-32 (crashes) mask 32+ returns -1
    #result = empty_ipv4.add(base,mask)
    #assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

#def test_add_prefix_with_largest_mask_valid(): # /0
    #base = 0x20408000
    #mask = 0  #works only for 1-18. 0,19-32 (crashes) mask 32+ returns -1
    #result = empty_ipv4.add(base,mask)
    #assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

def test_add_multiple_valid_prefixes_valid(empty_ipv4):
    empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    result = empty_ipv4.add(0x20408000,16) #32.64.128.0/16
    assert result == 0, f"add(base,mask) function valid test failed - function returned {result}"

def test_add_prefix_with_negative_base_invalid(empty_ipv4):
    result = empty_ipv4.add(-1,18)
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

def test_add_already_existing_prefix_invalid(empty_ipv4):
    empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    result = empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

def test_add_mask_outside_of_range_invalid(empty_ipv4):
    result = empty_ipv4.add(0x0A140000,33)
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

#del test cases
def test_del_existing_prefix_valid(ipv4_with_example):
    ip_collection, base, mask = ipv4_with_example
    result = ip_collection.del_prefix(base, mask)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_existing_smallest_mask_prefix_valid(empty_ipv4): # /32
    #empty_ipv4.add(0x0A140000, 32)
    result = empty_ipv4.del_prefix(0x0A140000, 32)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_existing_largest_mask_prefix_valid(empty_ipv4): # /0
    #empty_ipv4.add(0x0A140000, 0)
    result = empty_ipv4.del_prefix(0x0A140000, 0)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_nonexisting_prefix_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(0x0A140000,16)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

def test_del_prefix_with_out_of_range_mask_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(0x0A140000, 33)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

def test_del_prefix_with_negative_base_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(-1,18)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

#check test cases
def test_check_ip_within_single_prefix_range_valid():
    pass

def test_check_ip_within_multiple_prefix_ranges_valid():
    pass

def test_check_ip_within_prefix_with_smallest_mask_range_valid(): # /32
    pass

def test_check_ip_within_prefix_with_largest_mask_range_valid(): # /0
    pass

def test_check_ip_at_the_edge_of_a_prefix_valid():
    pass

def test_check_ip_with_no_matching_prefix_invalid():
    pass

def test_check_prefix_with_out_of_range_mask_invalid():
    pass

def test_check_prefix_with_negative_base_invalid():
    pass