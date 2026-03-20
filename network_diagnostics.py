#!/usr/bin/env python3
# Network Diagnostics Tool
"""
Network Diagnostic Tool - Ping, Traceroute, and Latency Check
A comprehensive tool for network diagnostics and monitoring.
"""

import subprocess
import platform
import sys
import json
import statistics
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re


@dataclass
class PingResult:
    """Data class for ping results."""
    host: str
    packets_sent: int
    packets_received: int
    packet_loss: float
    min_time: float
    max_time: float
    avg_time: float
    std_dev: float
    success: bool
    timestamp: str


@dataclass
class LatencyResult:
    """Data class for latency check results."""
    host: str
    port: int
    latencies: List[float]
    avg_latency: float
    min_latency: float
    max_latency: float
    std_dev: float
    packets_sent: int
    packets_received: int
    success: bool
    timestamp: str


@dataclass
class TracerouteResult:
    """Data class for traceroute results."""
    host: str
    hops: List[Dict]
    success: bool
    timestamp: str


class NetworkDiagnostics:
    """Main class for network diagnostics."""

    def __init__(self):
        self.system = platform.system()
        self.is_windows = self.system == "Windows"
        self.is_linux = self.system == "Linux"
        self.is_macos = self.system == "Darwin"

    def ping(self, host: str, count: int = 4, timeout: int = 4) -> PingResult:
        """
        Perform ping to a host.

        Args:
            host: Target hostname or IP address
            count: Number of ping packets
            timeout: Timeout in seconds

        Returns:
            PingResult object with ping statistics
        """
        try:
            # Build ping command based on OS
            if self.is_windows:
                cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(timeout), host]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout * count + 5
            )

            # Parse output
            output = result.stdout
            packets_sent = count
            packets_received = 0
            times = []
            packet_loss = 100.0

            if self.is_windows:
                # Windows ping output parsing
                packets_sent_match = re.search(
                    r"Packets: Sent = (\d+)", output
                )
                packets_received_match = re.search(
                    r"Received = (\d+)", output
                )
                time_matches = re.findall(r"time[<=](\d+)ms", output)

                if packets_sent_match:
                    packets_sent = int(packets_sent_match.group(1))
                if packets_received_match:
                    packets_received = int(packets_received_match.group(1))
                if time_matches:
                    times = [float(t) for t in time_matches]

            else:
                # Linux/macOS ping output parsing
                lines = output.split('\n')
                for line in lines:
                    if 'time=' in line:
                        match = re.search(r"time=(\d+\.?\d*)\s*ms", line)
                        if match:
                            times.append(float(match.group(1)))

                # Extract summary line
                for line in lines:
                    if 'received' in line or 'packets' in line:
                        received_match = re.search(r"(\d+) received", line)
                        if received_match:
                            packets_received = int(received_match.group(1))

            # Calculate statistics
            if packets_received == 0:
                return PingResult(
                    host=host,
                    packets_sent=packets_sent,
                    packets_received=packets_received,
                    packet_loss=100.0,
                    min_time=0.0,
                    max_time=0.0,
                    avg_time=0.0,
                    std_dev=0.0,
                    success=False,
                    timestamp=datetime.now().isoformat()
                )

            packet_loss = ((packets_sent - packets_received) / packets_sent) * 100
            avg_time = statistics.mean(times) if times else 0.0
            min_time = min(times) if times else 0.0
            max_time = max(times) if times else 0.0
            std_dev = statistics.stdev(times) if len(times) > 1 else 0.0

            return PingResult(
                host=host,
                packets_sent=packets_sent,
                packets_received=packets_received,
                packet_loss=packet_loss,
                min_time=min_time,
                max_time=max_time,
                avg_time=avg_time,
                std_dev=std_dev,
                success=packets_received > 0,
                timestamp=datetime.now().isoformat()
            )

        except subprocess.TimeoutExpired:
            return PingResult(
                host=host,
                packets_sent=count,
                packets_received=0,
                packet_loss=100.0,
                min_time=0.0,
                max_time=0.0,
                avg_time=0.0,
                std_dev=0.0,
                success=False,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            print(f"Error during ping: {e}", file=sys.stderr)
            return PingResult(
                host=host,
                packets_sent=count,
                packets_received=0,
                packet_loss=100.0,
                min_time=0.0,
                max_time=0.0,
                avg_time=0.0,
                std_dev=0.0,
                success=False,
                timestamp=datetime.now().isoformat()
            )

    def traceroute(self, host: str, max_hops: int = 30) -> TracerouteResult:
        """
        Perform traceroute to a host.

        Args:
            host: Target hostname or IP address
            max_hops: Maximum number of hops

        Returns:
            TracerouteResult object with hop information
        """
        try:
            if self.is_windows:
                cmd = ["tracert", "-h", str(max_hops), host]
            else:
                cmd = ["traceroute", "-m", str(max_hops), host]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            output = result.stdout
            hops = []

            if self.is_windows:
                # Windows tracert output parsing
                lines = output.split('\n')
                for line in lines:
                    if re.match(r'\s*\d+', line):
                        hop_match = re.match(
                            r'\s*(\d+)\s+(.+?)\s+(\[.+?\])?',
                            line
                        )
                        if hop_match:
                            hop_num = int(hop_match.group(1))
                            info = hop_match.group(2)
                            ip = hop_match.group(3)

                            times = re.findall(r'(\d+\s+ms)', info)
                            hops.append({
                                'hop': hop_num,
                                'times': times,
                                'info': info,
                                'ip': ip if ip else 'N/A'
                            })
            else:
                # Linux/macOS traceroute output parsing
                lines = output.split('\n')
                for line in lines:
                    if re.match(r'\s*\d+', line):
                        parts = line.split()
                        if len(parts) >= 2:
                            hop_num = int(parts[0])
                            host_info = ' '.join(parts[1:])

                            hops.append({
                                'hop': hop_num,
                                'host': host_info,
                                'info': line.strip()
                            })

            return TracerouteResult(
                host=host,
                hops=hops,
                success=len(hops) > 0,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"Error during traceroute: {e}", file=sys.stderr)
            return TracerouteResult(
                host=host,
                hops=[],
                success=False,
                timestamp=datetime.now().isoformat()
            )

    def check_latency(
        self,
        host: str,
        port: int = 80,
        count: int = 5,
        timeout: int = 5
    ) -> LatencyResult:
        """
        Check latency to a specific host and port using TCP connection.

        Args:
            host: Target hostname or IP address
            port: Target port
            count: Number of latency checks
            timeout: Timeout in seconds

        Returns:
            LatencyResult object with latency statistics
        """
        import socket

        latencies = []
        packets_received = 0

        for _ in range(count):
            try:
                start_time = time.time()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout)
                sock.connect((host, port))
                sock.close()
                end_time = time.time()

                latency = (end_time - start_time) * 1000  # Convert to ms
                latencies.append(latency)
                packets_received += 1

            except socket.timeout:
                pass
            except Exception:
                pass

            time.sleep(0.1)

        if packets_received == 0:
            return LatencyResult(
                host=host,
                port=port,
                latencies=[],
                avg_latency=0.0,
                min_latency=0.0,
                max_latency=0.0,
                std_dev=0.0,
                packets_sent=count,
                packets_received=packets_received,
                success=False,
                timestamp=datetime.now().isoformat()
            )

        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        std_dev = statistics.stdev(latencies) if len(latencies) > 1 else 0.0

        return LatencyResult(
            host=host,
            port=port,
            latencies=latencies,
            avg_latency=avg_latency,
            min_latency=min_latency,
            max_latency=max_latency,
            std_dev=std_dev,
            packets_sent=count,
            packets_received=packets_received,
            success=True,
            timestamp=datetime.now().isoformat()
        )


class ResultFormatter:
    """Format and display results."""

    @staticmethod
    def format_ping(result: PingResult) -> str:
        """Format ping result for display."""
        status = "✓ Success" if result.success else "✗ Failed"
        
        output = f"""
╔═══════════════════════════════════════════════════════╗
║               PING RESULTS - {status}                 ║
╚═══════════════════════════════════════════════════════╝

Host:               {result.host}
Packets Sent:       {result.packets_sent}
Packets Received:   {result.packets_received}
Packet Loss:        {result.packet_loss:.2f}%

Latency Statistics (ms):
  Minimum:          {result.min_time:.2f}
  Maximum:          {result.max_time:.2f}
  Average:          {result.avg_time:.2f}
  Std Dev:          {result.std_dev:.2f}

Timestamp:          {result.timestamp}
"""
        return output

    @staticmethod
    def format_traceroute(result: TracerouteResult) -> str:
        """Format traceroute result for display."""
        status = "✓ Success" if result.success else "✗ Failed"
        
        output = f"""
╔════════════════════════════════════════════════════════╗
║           TRACEROUTE RESULTS - {status}                ║
╚════════════════════════════════════════════════════════╝

Host:               {result.host}
Total Hops:         {len(result.hops)}

Hops:
"""
        for hop in result.hops[:15]:  # Limit to first 15 hops
            output += f"  {hop.get('hop', 'N/A')}: {hop.get('info', hop.get('host', 'N/A'))}\n"

        output += f"\nTimestamp:          {result.timestamp}\n"
        return output

    @staticmethod
    def format_latency(result: LatencyResult) -> str:
        """Format latency result for display."""
        status = "✓ Success" if result.success else "✗ Failed"
        
        output = f"""
╔════════════════════════════════════════════════════════╗
║            LATENCY RESULTS - {status}                  ║
╚════════════════════════════════════════════════════════╝

Host:               {result.host}:{result.port}
Packets Sent:       {result.packets_sent}
Packets Received:   {result.packets_received}

Latency Statistics (ms):
  Minimum:          {result.min_latency:.2f}
  Maximum:          {result.max_latency:.2f}
  Average:          {result.avg_latency:.2f}
  Std Dev:          {result.std_dev:.2f}

Detailed Latencies: {[f'{l:.2f}' for l in result.latencies]}

Timestamp:          {result.timestamp}
"""
        return output

    @staticmethod
    def to_json(result) -> str:
        """Convert result to JSON format."""
        return json.dumps(asdict(result), indent=2)


def main():
    """Main function with CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Network Diagnostic Tool - Ping, Traceroute, and Latency Check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python network_diagnostics.py ping google.com
  python network_diagnostics.py ping google.com -c 10
  python network_diagnostics.py traceroute google.com
  python network_diagnostics.py latency google.com -p 443
  python network_diagnostics.py latency google.com -p 80 -c 10
  python network_diagnostics.py all google.com
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Ping command
    ping_parser = subparsers.add_parser('ping', help='Ping a host')
    ping_parser.add_argument('host', help='Target hostname or IP address')
    ping_parser.add_argument('-c', '--count', type=int, default=4,
                            help='Number of ping packets (default: 4)')
    ping_parser.add_argument('-t', '--timeout', type=int, default=4,
                            help='Timeout in seconds (default: 4)')
    ping_parser.add_argument('-j', '--json', action='store_true',
                            help='Output as JSON')

    # Traceroute command
    traceroute_parser = subparsers.add_parser('traceroute', help='Traceroute to a host')
    traceroute_parser.add_argument('host', help='Target hostname or IP address')
    traceroute_parser.add_argument('-m', '--max-hops', type=int, default=30,
                                  help='Maximum number of hops (default: 30)')
    traceroute_parser.add_argument('-j', '--json', action='store_true',
                                  help='Output as JSON')

    # Latency command
    latency_parser = subparsers.add_parser('latency', help='Check latency to a host')
    latency_parser.add_argument('host', help='Target hostname or IP address')
    latency_parser.add_argument('-p', '--port', type=int, default=80,
                               help='Target port (default: 80)')
    latency_parser.add_argument('-c', '--count', type=int, default=5,
                               help='Number of latency checks (default: 5)')
    latency_parser.add_argument('-t', '--timeout', type=int, default=5,
                               help='Timeout in seconds (default: 5)')
    latency_parser.add_argument('-j', '--json', action='store_true',
                               help='Output as JSON')

    # All diagnostics command
    all_parser = subparsers.add_parser('all', help='Run all diagnostics')
    all_parser.add_argument('host', help='Target hostname or IP address')
    all_parser.add_argument('-j', '--json', action='store_true',
                           help='Output as JSON')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    diagnostics = NetworkDiagnostics()
    formatter = ResultFormatter()

    try:
        if args.command == 'ping':
            result = diagnostics.ping(args.host, args.count, args.timeout)
            output = formatter.to_json(result) if args.json else formatter.format_ping(result)
            print(output)

        elif args.command == 'traceroute':
            result = diagnostics.traceroute(args.host, args.max_hops)
            output = formatter.to_json(result) if args.json else formatter.format_traceroute(result)
            print(output)

        elif args.command == 'latency':
            result = diagnostics.check_latency(
                args.host, args.port, args.count, args.timeout
            )
            output = formatter.to_json(result) if args.json else formatter.format_latency(result)
            print(output)

        elif args.command == 'all':
            print("Running all diagnostics...")
            ping_result = diagnostics.ping(args.host, count=4)
            print(formatter.format_ping(ping_result))

            traceroute_result = diagnostics.traceroute(args.host)
            print(formatter.format_traceroute(traceroute_result))

            latency_result = diagnostics.check_latency(args.host, port=80, count=5)
            print(formatter.format_latency(latency_result))

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
