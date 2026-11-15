"""Explicit real-owner HTTP fixture for pre-ISP specialist inspection tests.

Import the dependencies with inspection_web into the requesting test module.
No route-based elevation, forged headers or production credentials are used.
"""
import pytest
from tests.test_flora_security_repair_01b import authority
from tests.test_flora_sales_pipeline import actor,web as owner_http

@pytest.fixture
def inspection_web(owner_http):
    return lambda path:owner_http(path)[:2]
