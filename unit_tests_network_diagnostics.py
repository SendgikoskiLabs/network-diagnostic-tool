#!/usr/bin/env python3
"""
Unit tests for Network Diagnostic Tool
"""

import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from network_diagnostics import (
    NetworkDiagnostics,
    PingResult,
    LatencyResult,
    TracerouteResult,
    ResultFormatter
)


class TestNetworkDiagnostics(unittest.TestCase):
    """Test cases for NetworkDiagnostics class."""

    def setUp(self):
        """Set up test fixtures."""
        self.diagnostics = NetworkDiagnostics()

    def test_ping_localhost(self):
        """Test ping to localhost."""
        result = self.diagnostics.ping('localhost', count=2)
        self.assertIsInstance(result, PingResult)
        self.assertEqual(result.host, 'localhost')
        self.assertEqual(result.packets_sent, 2)

    def test_ping_result_attributes(self):
        """Test PingResult has all required attributes."""
        result = self.diagnostics.ping('127.0.0.1', count=2)
        self.assertTrue(hasattr(result, 'host'))
        self.assertTrue(hasattr(result, 'packets_sent'))
        self.assertTrue(hasattr(result, 'packets_received'))
        self.assertTrue(hasattr(result, 'packet_loss'))
        self.assertTrue(hasattr(result, 'min_time'))
        self.assertTrue(hasattr(result, 'max_time'))
        self.assertTrue(hasattr(result, 'avg_time'))
        self.assertTrue(hasattr(result, 'std_dev'))
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'timestamp'))

    def test_latency_result_attributes(self):
        """Test LatencyResult has all required attributes."""
        result = self.diagnostics.check_latency('localhost', port=22, count=2)
        self.assertIsInstance(result, LatencyResult)
        self.assertTrue(hasattr(result, 'host'))
        self.assertTrue(hasattr(result, 'port'))
        self.assertTrue(hasattr(result, 'latencies'))
        self.assertTrue(hasattr(result, 'avg_latency'))
        self.assertTrue(hasattr(result, 'min_latency'))
        self.assertTrue(hasattr(result, 'max_latency'))

    def test_traceroute_result_attributes(self):
        """Test TracerouteResult has all required attributes."""
        result = self.diagnostics.traceroute('localhost', max_hops=10)
        self.assertIsInstance(result, TracerouteResult)
        self.assertTrue(hasattr(result, 'host'))
        self.assertTrue(hasattr(result, 'hops'))
        self.assertTrue(hasattr(result, 'success'))
        self.assertTrue(hasattr(result, 'timestamp'))

    def test_formatter_ping(self):
        """Test ResultFormatter ping formatting."""
        result = self.diagnostics.ping('localhost', count=2)
        formatter = ResultFormatter()
        output = formatter.format_ping(result)
        self.assertIsInstance(output, str)
        self.assertIn('PING RESULTS', output)
        self.assertIn('localhost', output)

    def test_formatter_latency(self):
        """Test ResultFormatter latency formatting."""
        result = self.diagnostics.check_latency('localhost', count=2)
        formatter = ResultFormatter()
        output = formatter.format_latency(result)
        self.assertIsInstance(output, str)
        self.assertIn('LATENCY RESULTS', output)
        self.assertIn('localhost', output)

    def test_formatter_traceroute(self):
        """Test ResultFormatter traceroute formatting."""
        result = self.diagnostics.traceroute('localhost', max_hops=5)
        formatter = ResultFormatter()
        output = formatter.format_traceroute(result)
        self.assertIsInstance(output, str)
        self.assertIn('TRACEROUTE RESULTS', output)
        self.assertIn('localhost', output)

    def test_to_json(self):
        """Test JSON conversion."""
        result = self.diagnostics.ping('localhost', count=2)
        formatter = ResultFormatter()
        json_output = formatter.to_json(result)
        self.assertIsInstance(json_output, str)
        self.assertIn('"host"', json_output)
        self.assertIn('localhost', json_output)


class TestPingResult(unittest.TestCase):
    """Test cases for PingResult dataclass."""

    def test_ping_result_creation(self):
        """Test PingResult creation."""
        result = PingResult(
            host='test.com',
            packets_sent=4,
            packets_received=4,
            packet_loss=0.0,
            min_time=10.0,
            max_time=20.0,
            avg_time=15.0,
            std_dev=3.5,
            success=True,
            timestamp='2026-03-20T12:00:00'
        )
        self.assertEqual(result.host, 'test.com')
        self.assertEqual(result.packets_sent, 4)
        self.assertTrue(result.success)


class TestLatencyResult(unittest.TestCase):
    """Test cases for LatencyResult dataclass."""

    def test_latency_result_creation(self):
        """Test LatencyResult creation."""
        result = LatencyResult(
            host='test.com',
            port=80,
            latencies=[10.5, 11.2, 10.8],
            avg_latency=10.83,
            min_latency=10.5,
            max_latency=11.2,
            std_dev=0.35,
            packets_sent=3,
            packets_received=3,
            success=True,
            timestamp='2026-03-20T12:00:00'
        )
        self.assertEqual(result.host, 'test.com')
        self.assertEqual(result.port, 80)
        self.assertEqual(len(result.latencies), 3)


if __name__ == '__main__':
    unittest.main()
