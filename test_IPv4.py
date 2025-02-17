from ctypes import CDLL
import ctypes
import pytest
import logging

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
ipv4.check.restype = ctypes.c_char # return type: char

# Configure the logger
logger = logging.getLogger(__name__)

@pytest.fixture(scope="session", autouse=True)
def setup_logging():
    logger.setLevel(logging.INFO)

    # Remove existing handlers to prevent duplicates
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)


#helper functions 
def ip_to_int(ip_str):
    parts = list(map(int, ip_str.split(".")))  # split string by dot into 4
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

def int_to_byte(value, byte_length=1, byteorder='big', signed=True):
    try:
        return value.to_bytes(byte_length, byteorder=byteorder, signed=signed)
    except OverflowError:
        raise ValueError(f"Value {value} cannot be represented in {byte_length} byte(s) with signed={signed}")

def add_prefixes(prefixes, count):
    base = 0x0A140000  # 10.20.0.0 as a c_uint value
    mask = 16  # /16 mask
    
    for i in range(count):  # Try adding the prefix 64 times
        result = prefixes.add(base + i, mask)
        if result == -1:
            logger.info(f"Failed to add prefix {base + i}/{mask} at iteration {i+1}")
            break  # Stop if the function returns -1 (failure)
        logger.info(f"Added prefix {base + i}/{mask} successfully ({i+1}/64)")
    return 0

'''
def test_add_all_masks(): #Crashes on the first mask (0)
    base = 0x0A140000
    print(f"Testing masks for base: {base} (0x{base:08x})")
    for mask in range(33):  # Maski od 0 do 32
        try:
            print(f"Attempting to add mask: {mask}")
            result = ipv4.add(base, mask)
            print(f"Mask: {mask:2d}, Return: {result}")
        except Exception as e:
            print(f"Mask: {mask:2d}, Error: {str(e)}")
            pytest.fail(f"Test failed for mask {mask}: {str(e)}")
'''

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
    assert result == 0, f"add(base,mask) function valid test failed - function returned {result}"

def test_add_prefix_with_mask_1_valid(empty_ipv4):
    base = 0x20408000
    mask = 1  #works only for mask 8, 16 - crashes for 0,14,15,19-32
    result = empty_ipv4.add(base,int_to_byte(mask))
    assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

#def test_add_prefix_with_smallest_mask_valid(empty_ipv4):
    #base = 0x20408000
    #mask = 32  #works only for mask 8, 16 - crashes for 0,14,15,19-32
    #result = empty_ipv4.add(base,mask)
    #assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

#def test_add_prefix_with_largest_mask_valid(): # /0
    #base = 0x20408000
    #mask = 0  #works only for mask 8, 16 - crashes for 0,14,15,19-32
    #result = empty_ipv4.add(base,mask)
    #assert result == 0, f"add({base},{mask}) function valid test failed - function returned {result}"

def test_add_multiple_valid_prefixes_valid(empty_ipv4):
    empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    result = empty_ipv4.add(0x20408000,16) #32.64.128.0/16
    assert result == 0, f"add(base,mask) function valid test failed - function returned {result}"

def test_add_max_prefixes_valid(empty_ipv4):
    count = 64
    result = add_prefixes(empty_ipv4, count)
    assert result == 0, f"add(base,mask) x {count} times function valid test failed - function returned {result}"

def test_add_ip_as_none_invalid(empty_ipv4):
    with pytest.raises(ctypes.ArgumentError):
        empty_ipv4.add(None, 16)

def test_add_mask_as_none_invalid(empty_ipv4):
    with pytest.raises(ctypes.ArgumentError):
        empty_ipv4.add(0x0A140000, None)

def test_add_prefixes_over_the_limit_invalid(empty_ipv4):
    count = 65
    result = add_prefixes(empty_ipv4, count)
    assert result == -1, f"add(base,mask) x {count} (limit=64) times function invalid test failed - function returned {result}"

def test_add_prefix_with_negative_base_invalid(empty_ipv4):
    result = empty_ipv4.add(-1,18)
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

def test_add_mask_wtih_negative_value_invalid(empty_ipv4):
    result = empty_ipv4.add(0x0A140000, -1)  # Negative mask
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}, expected -1"

def test_add_already_existing_prefix_invalid(empty_ipv4):
    empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    result = empty_ipv4.add(0x0A140000,16) #10.20.0.0/16
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

def test_add_mask_outside_of_range_invalid(empty_ipv4):
    result = empty_ipv4.add(0x0A140000,33)
    assert result == -1, f"add(base,mask) function invalid test failed - function returned {result}"

def test_add_ip_as_a_string_invalid(empty_ipv4):
    with pytest.raises(TypeError):
        empty_ipv4.add("not_an_ip", 16)

#del test cases
def test_del_existing_prefix_valid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    result = ip_prefixes.del_prefix(base, mask)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_existing_smallest_mask_prefix_valid(empty_ipv4): # /32
    #empty_ipv4.add(0x0A140000, 32)
    result = empty_ipv4.del_prefix(0x0A140000, 32)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_existing_largest_mask_prefix_valid(empty_ipv4): # /0
    #empty_ipv4.add(0x0A140000, 0)
    result = empty_ipv4.del_prefix(0x0A140000, 0)
    assert result == 0, f"del(base,mask) function valid test failed - function returned {result}"

def test_del_existing_prefix_with_mask_1_valid(empty_ipv4):  # /1
    base = 0x0A140000
    mask = 1
    result = empty_ipv4.del_prefix(base, mask)
    assert result == 0, f"del({base},{mask}) function valid test failed - function returned {result}"

def test_del_nonexisting_prefix_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(0x0A140000,16)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

def test_del_prefix_with_out_of_range_mask_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(0x0A140000, 33)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

def test_del_prefix_with_negative_base_invalid(empty_ipv4):
    result = empty_ipv4.del_prefix(-1,18)
    assert result == -1, f"del(base,mask) function invalid test failed - function returned {result}"

def test_del_ip_as_a_string_invalid(empty_ipv4):
    with pytest.raises(ctypes.ArgumentError):
        empty_ipv4.del_prefix("not_an_ip", 16)

def test_del_invalid_mask_string_invalid(empty_ipv4):
    with pytest.raises(ctypes.ArgumentError):
        empty_ipv4.del_prefix(0x0A140000, "not_a_mask")

#check test cases
def test_check_ip_within_single_prefix_range_valid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    check_prefix = 0x0a14ff01 #10.20.255.1
    result = ip_prefixes.check(check_prefix)   
    result_int = int.from_bytes(result, byteorder='big', signed=True) #in python c_char return byte (example: returns b'\xff' instead of -1)
    assert result_int == mask, f"check(ip) function valid test failed - function returned {result_int}, expected {mask}"

def test_check_ip_equal_to_base_valid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    result = ip_prefixes.check(base)  #IP equal to base
    result_int = int.from_bytes(result, byteorder='big', signed=True)
    assert result_int == mask, f"check(ip) function valid test failed - function returned {result_int}, expected {mask}"

def test_check_ip_within_multiple_prefix_ranges_valid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    base2 = 0x0a140100 # 10.20.1.0
    mask2 = 18
    ip_prefixes.add(base2,mask2)
    result = ip_prefixes.check(base2)
    result_int = int.from_bytes(result, byteorder='big', signed=True) 
    assert result_int == mask2, f"check(ip) function valid test failed - function returned {result_int}, expected {mask2}"

def test_check_ip_at_the_edge_of_a_prefix_valid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    result = ip_prefixes.check(0x0a14ffff) # 10.20.255.255
    result_int = int.from_bytes(result, byteorder='big', signed=True) 
    assert result_int == mask, f"check(ip) function valid test failed - function returned {result_int}, expected {mask}"

def test_check_ip_just_outside_prefix_range_invalid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    ip = 0x0a150000  #just outside of the 10.20.0.0/16 range - 10.21.0.0
    result = ip_prefixes.check(ip)
    result_int = int.from_bytes(result, byteorder='big', signed=True)
    assert result_int == -1, f"check(ip) function invalid test failed - function returned {result_int}, expected -1"

def test_check_ip_with_no_matching_prefix_invalid(ipv4_with_example):
    ip_prefixes, base, mask = ipv4_with_example
    result = ip_prefixes.check(0x0a150001) #10.21.0.1
    result_int = int.from_bytes(result, byteorder='big', signed=True) 
    assert result_int == -1, f"check(ip) function invalid test failed - function returned {result_int}, expected -1"

def test_check_prefix_with_negative_base_invalid(empty_ipv4):
    result = empty_ipv4.check(-1)
    result_int = int.from_bytes(result, byteorder='big', signed=True)
    assert result_int == -1, f"check(ip) function invalid test failed - function returned {result_int}, expected -1"