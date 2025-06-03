# Deployment Guide for Distributed Hashcat Cracking System

This guide provides detailed instructions for deploying the distributed cracking system across multiple nodes with different GPU types.

## Deployment Scenarios

### Local Development Setup
- Single machine running both server and agent
- Useful for testing and development
- No network configuration required

### Multi-Node Local Network Deployment
- Management server on one machine
- Multiple agent nodes on the same local network
- Ideal for small-scale deployments

### Hybrid Cloud Deployment
- Management server on local machine
- Agent nodes on both local network and cloud servers
- Combines on-premises and cloud resources

### Full Cloud Deployment
- All components running in cloud environments
- Maximum scalability and flexibility

## Multi-Node Deployment with Different GPU Types

The system is designed to work with heterogeneous GPU environments, allowing you to leverage different types of GPUs (AMD, NVIDIA) across multiple nodes.

### Example Setup: Local AMD GPU + Cloud NVIDIA GPU

This configuration uses a local mini PC with AMD GPU as both the management server and the first cracking node, plus a cloud server with NVIDIA GPU as an additional cracking node.

#### 1. Management Server + Node 1 (Local Mini PC with AMD GPU)

1. **Install Dependencies**
   ```bash
   # Install hashcat with AMD GPU support
   sudo apt install hashcat ocl-icd-opencl-dev
   
   # Verify GPU detection
   hashcat -I
   ```

2. **Start Management Server**
   ```bash
   # Start the central server
   python -m cmd.server
   
   # Start the web dashboard (in a separate terminal)
   python -m cmd.web
   ```

3. **Start Local Agent (Node 1)**
   ```bash
   # Start agent on the same machine
   python -m cmd.agent --server-url http://localhost:8082 --name "local-amd-node"
   ```

#### 2. Node 2 (Cloud Server with NVIDIA GPU)

1. **Setup Environment**
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/distributed-cracking.git
   cd distributed-cracking
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install hashcat with NVIDIA support
   sudo apt install hashcat nvidia-opencl-dev
   
   # Verify GPU detection
   hashcat -I
   ```

2. **Configure Environment**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env file to match your setup
   # No need to configure MongoDB settings on agent nodes
   ```

3. **Start Remote Agent**
   ```bash
   # Connect to management server (replace with your Mini PC's IP address)
   python -m cmd.agent --server-url http://192.168.1.100:8082 --name "cloud-nvidia-node"
   ```

### Network Configuration

1. **Firewall Settings**
   - Ensure port 8082 (or your configured SERVER_PORT) is open on the management server
   - For internet-facing deployments, consider using a VPN or SSH tunnel for security

2. **Security Considerations**
   - The agent-server communication uses API keys generated during registration
   - For production environments, consider enabling HTTPS with valid certificates
   - Implement network-level security (firewall rules, VPN) for public cloud deployments

### Monitoring Multiple Nodes

The web dashboard provides a unified view of all connected agents:

1. Navigate to the **Agents** section in the web dashboard
2. View detailed information about each agent including:
   - GPU type and capabilities
   - Current status and workload
   - Performance metrics

### Task Distribution Strategy

The system automatically distributes tasks based on agent availability and capabilities:

1. **Auto-Assignment**: Tasks are automatically assigned to available agents
2. **Manual Assignment**: Administrators can manually assign specific tasks to specific agents
3. **GPU-Specific Tasks**: Some hash types perform better on specific GPU architectures

## Connecting to a Public Cloud GPU Server

If your GPU server has a public IP address (e.g., a cloud instance), follow these steps to securely connect it to your management server:

### Management Server (Mini PC) Configuration

1. **Make Your Management Server Accessible**
   ```bash
   # Option 1: Port forwarding on your router (port 8082)
   # Configure your router to forward port 8082 to your mini PC's local IP
   
   # Option 2: Use ngrok for temporary access
   ngrok http 8082
   # Note the generated URL (e.g., https://a1b2c3d4.ngrok.io)
   ```

2. **Enable HTTPS for Security (Recommended)**
   ```bash
   # Generate self-signed certificate
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
   
   # Update .env configuration
   echo "USE_HTTPS=true" >> .env
   echo "SSL_CERT_FILE=cert.pem" >> .env
   echo "SSL_KEY_FILE=key.pem" >> .env
   ```

3. **Configure Server to Listen on All Interfaces**
   ```bash
   # Edit .env file
   echo "SERVER_HOST=0.0.0.0" >> .env
   ```

### Remote GPU Server Configuration

1. **Minimal Configuration**
   ```bash
   # Create minimal .env file
   echo "HASHCAT_PATH=/usr/bin/hashcat" > .env
   echo "AGENT_POLL_INTERVAL=5" >> .env
   echo "AGENT_HEARTBEAT_INTERVAL=30" >> .env
   ```

2. **Connect to Management Server**
   ```bash
   # If using HTTPS with public IP
   python -m cmd.agent --server-url https://YOUR_PUBLIC_IP:8082 --name "cloud-nvidia-node" --verify-ssl false
   
   # If using ngrok
   python -m cmd.agent --server-url https://YOUR_NGROK_URL --name "cloud-nvidia-node"
   ```

### Security Recommendations

1. **Use a VPN** between your mini PC and cloud server
   - Set up WireGuard or OpenVPN for secure communication
   - Run all agent-server traffic through the VPN tunnel

2. **Implement IP Restrictions**
   ```bash
   # On cloud server, restrict outgoing connections
   sudo iptables -A OUTPUT -p tcp -d YOUR_MINI_PC_IP --dport 8082 -j ACCEPT
   sudo iptables -A OUTPUT -p tcp -j DROP
   ```

3. **Use Strong API Keys**
   - The system automatically generates API keys during agent registration
   - Store these securely and rotate them periodically

### Example Configuration Files

**Mini PC Management Server (.env)**:
```
# Server settings
SERVER_HOST=0.0.0.0
SERVER_PORT=8082
USE_HTTPS=true
SSL_CERT_FILE=cert.pem
SSL_KEY_FILE=key.pem

# Database settings
USE_MOCK_DATABASE=true  # or false if using MongoDB
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=hashcat_cracking

# Hashcat settings
HASHCAT_PATH=/usr/bin/hashcat
```

**Cloud GPU Server (.env)**:
```
# Agent settings
AGENT_POLL_INTERVAL=5
AGENT_HEARTBEAT_INTERVAL=30

# Hashcat settings
HASHCAT_PATH=/usr/bin/hashcat
```

## Scaling the Deployment

### Adding More Agent Nodes

To add additional agent nodes to your deployment:

1. Clone the repository on the new node
2. Install dependencies and hashcat
3. Configure the .env file with minimal agent settings
4. Start the agent with the appropriate server URL

### Load Balancing Considerations

The system automatically distributes tasks based on agent availability, but consider:

- Assigning specific hash types to specific GPU architectures for optimal performance
- Monitoring agent performance and adjusting task assignments accordingly
- For very large deployments, consider implementing a dedicated load balancer

## Troubleshooting Deployment Issues

### Connectivity Problems

- Verify firewall settings on both server and agent nodes
- Check network connectivity between nodes
- Ensure the server is listening on the correct interface (0.0.0.0 for external access)

### Agent Registration Issues

- Verify the server URL is correct and accessible
- Check for SSL certificate issues (use --verify-ssl false for self-signed certificates)
- Ensure the agent has a unique name

### Performance Optimization

- Adjust AGENT_POLL_INTERVAL and AGENT_HEARTBEAT_INTERVAL based on network latency
- Monitor GPU utilization and adjust task size accordingly
- Consider network bandwidth limitations when distributing large wordlists
