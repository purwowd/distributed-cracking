# Distributed Hashcat Cracking System Documentation

This directory contains comprehensive documentation for the Distributed Hashcat Cracking System. Each document focuses on a specific aspect of the system to provide clear, targeted information.

## Documentation Contents

### [Main README](../README.md)
- System overview and features
- Quick start guide
- Basic architecture
- Requirements and installation

### [Deployment Guide](deployment.md)
- Multi-node deployment scenarios
- Heterogeneous GPU environment setup (AMD + NVIDIA)
- Cloud GPU server integration
- Network configuration
- Example configuration files

### [MongoDB Configuration](mongodb.md)
- Installation and setup
- Database initialization scripts
- User management
- Migration from mock database
- Performance optimization
- Backup and recovery

### [Security Guidelines](security.md)
- Authentication and authorization
- Network security best practices
- Public-facing deployment considerations
- Data protection measures
- Operational security

### [Web Interface](web_interface.md)
- Dashboard features and navigation
- Task creation and management
- Agent monitoring
- Results viewing
- Login system
- Troubleshooting

## Getting Started

If you're new to the system:

1. Start with the [Main README](../README.md) for an overview
2. Follow the [Deployment Guide](deployment.md) to set up your environment
3. Configure your database using [MongoDB Configuration](mongodb.md)
4. Implement security measures from [Security Guidelines](security.md)
5. Learn how to use the system with [Web Interface](web_interface.md)

## Developer Documentation

For developers who want to modify or extend the system:

- [Web Interface Technical Documentation](../cmd/web/README.md) - Structure, technologies, and extension guidelines for the web interface
