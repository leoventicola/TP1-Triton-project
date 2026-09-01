import argparse

import pytest

from triton_telemetry.sanitizer import parse_cluster_id, parse_timeout


@pytest.mark.parametrize(
    "value, expected",
    [
        ("0.1", 0.1),
        ("2.5", 2.5),
        ("5.0", 5.0),
    ],
)
def test_parse_timeout_valid(value, expected):
    assert parse_timeout(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        "0.0",
        "0.09",
        "5.1",
        "abc",
    ],
)
def test_parse_timeout_invalid(value):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_timeout(value)


def test_parse_cluster_id_valid():
    assert parse_cluster_id("cluster-us-east-01") == "cluster-us-east-01"


@pytest.mark.parametrize(
    "value",
    [
        "cluster-US-east-01",
        "cluster-u-east-01",
        "cluster-us-east-1",
        "cluster-us-east-001",
        "cluster-us-01",
    ],
)
def test_parse_cluster_id_invalid(value):
    with pytest.raises(argparse.ArgumentTypeError):
        parse_cluster_id(value)