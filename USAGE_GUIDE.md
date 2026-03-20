# Network Diagnostic Tool Usage Guide

## Introduction
The Network Diagnostic Tool is designed to help users troubleshoot network issues by providing various diagnostics and tools.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/SendgikoskiLabs/network-diagnostic-tool.git
   ```

2. Navigate to the project directory:
   ```bash
   cd network-diagnostic-tool
   ```

3. Install dependencies (if any).

## Usage
### Running the Tool
To run the Network Diagnostic Tool, use the following command:
```bash
python main.py
```

### Available Commands
- **ping:** Check the reachability of a host on the network.
  ```bash
  ping [hostname]
  ```

- **traceroute:** Display the path packets take to a network host.
  ```bash
  traceroute [hostname]
  ```

- **nslookup:** Query the DNS records of a domain.
  ```bash
  nslookup [domain]
  ```

- **bandwidth test:** Measure the bandwidth of your internet connection.
  ```bash
  bandwidth-test
  ```

## Examples
- To ping Google:
  ```bash
  ping google.com
  ```

- To perform a traceroute to example.com:
  ```bash
  traceroute example.com
  ```

## Troubleshooting
- Ensure you have the necessary permissions to execute network commands.
- If you encounter any issues, check the output for error messages.

## Conclusion
This guide provides a basic overview of how to install and use the Network Diagnostic Tool. For further assistance, refer to the project's documentation or raise an issue on GitHub.