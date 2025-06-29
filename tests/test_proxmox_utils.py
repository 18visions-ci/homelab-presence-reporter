import pytest
from unittest.mock import MagicMock
from src.proxmox_utils import _format_uptime, _get_pve_report, _get_pbs_report

def test_format_uptime():
    assert _format_uptime(0) == "0m"
    assert _format_uptime(59) == "0m"
    assert _format_uptime(60) == "1m"
    assert _format_uptime(3600) == "1h 0m"
    assert _format_uptime(86400) == "1d 0h 0m"
    assert _format_uptime(90061) == "1d 1h 1m"

def test_get_pve_report():
    mock_proxmox = MagicMock()
    mock_proxmox.nodes.get.return_value = [
        {"node": "pve1"},
        {"node": "pve2"},
        {"node": "pve3"}
    ]

    mock_proxmox.nodes.return_value.status.get.side_effect = [
        {
            "cpu": 0.5,
            "memory": {"used": 8e9, "total": 16e9},
            "rootfs": {"used": 20e9, "total": 100e9},
            "uptime": 90061
        },
        {
            "cpu": None,
            "memory": {"used": 8e9, "total": 16e9},
            "rootfs": {"used": 20e9, "total": 100e9},
            "uptime": 90061
        },
        Exception("API Error")
    ]

    report = _get_pve_report(mock_proxmox)
    assert "pve1" in report
    assert "50.0%" in report
    assert "8.0/16.0 GB" in report
    assert "20.0/100.0 GB" in report
    assert "1d 1h 1m" in report
    assert "pve2" in report
    assert "Missing metrics" in report
    assert "pve3" in report
    assert "Error: API Error" in report

def test_get_pbs_report():
    mock_pbs = MagicMock()
    mock_pbs.admin.datastore.get.return_value = [
        {"store": "datastore1"},
        {"store": "datastore2"}
    ]

    mock_pbs.admin.datastore.return_value.status.get.side_effect = [
        {
            "used": 500e9,
            "total": 1e12
        },
        {
            "used": None,
            "total": 1e12
        }
    ]

    mock_pbs.admin.datastore.return_value.snapshots.get.side_effect = [
        [
            {"backup-time": 1678886400, "backup-type": "vm", "backup-id": "100"}
        ],
        Exception("API Error")
    ]

    report = _get_pbs_report(mock_pbs)
    assert "datastore1" in report
    assert "500.0 GB" in report
    assert "1000.0 GB" in report
    assert "vm/100" in report
    assert "datastore2" in report
    assert "N/A" in report
