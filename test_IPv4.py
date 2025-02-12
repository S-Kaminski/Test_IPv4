from ctypes import CDLL
import ctypes

ipv4 = CDLL("./IPv4.so")

#int add(unsigned int base, char mask) 
ipv4.add.argtypes = [ctypes.c_uint, ctypes.c_char] #uint, char
ipv4.add.restype = ctypes.c_int  # return type: int

#helper function - ip converter
def ip_to_int(ip_str):
    parts = list(map(int, ip_str.split(".")))  # split string by dot into 4
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

def test_add_valid():
    base = ip_to_int("10.20.0.0")
    mask = 16
    result = ipv4.add(base,mask)
    assert result == 0, f"Add valid test (1) failed | base: {hex(base)}, mask: {mask} "

def test_add_invalid():
    base = ip_to_int("10.20.0.0")
    mask = 33  #invalid mask (valid range: 0-32)
    result = ipv4.add(base,mask)
    assert result == -1, f"Add invalid test (1) failed | base: {hex(base)}, mask: {mask} "

