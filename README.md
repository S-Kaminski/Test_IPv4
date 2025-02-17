# IPv4 Prefix Management Tests

## Project Overview

This project provides an interface to interact with an IPv4 shared objects (.so) using a shared C library (`IPv4.so`). It includes Python bindings to call C functions and a test suite using `pytest`.

---

## Installation Guide

### 1. Install System Dependencies

Ensure you have Python 3 and `venv` installed. If not, install them (venv is included in package with python 3.3+):

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

### 2. Clone the Repository

```bash
git clone https://github.com/S-Kaminski/Test_IPv4.git
cd Test_IPv4
```

### 3. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate 
```

### 4. Install Required Python Packages

```bash
pip install --upgrade pip
pip install pytest pytest-html pytest-metadata pytest-logging
```

---

## Running Tests

### 1. Execute Tests

```bash
pytest -v
```

### 2. Generate an HTML Report

To generate a detailed test report:

```bash
pytest --html=report.html --self-contained-html
```
(thanks to pytest.ini report automatically generates just by running pytest - must be in a virtual environment to run)

After execution, open `report.html` in a browser to view the results.

---
