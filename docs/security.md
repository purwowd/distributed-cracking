# Security Considerations for Distributed Hashcat Cracking System

This document outlines security considerations and best practices for deploying and operating the distributed cracking system in various environments.

## Authentication and Authorization

### User Authentication

The system uses a robust authentication system with the following features:

1. **JWT-based Authentication**
   - JSON Web Tokens (JWT) for secure session management
   - Tokens stored in HTTP-only cookies to prevent XSS attacks
   - Configurable token expiration (default: 24 hours)

2. **Password Security**
   - Passwords hashed using bcrypt with appropriate work factor
   - Minimum password strength requirements
   - Protection against brute force attacks

3. **Role-based Access Control**
   - Three user roles: admin, user, viewer
   - Granular permissions based on role
   - Resource-level access control

### API Authentication

Agent-server communication is secured through:

1. **API Key Authentication**
   - Unique API keys generated for each agent
   - Keys transmitted in HTTP headers
   - Regular key rotation recommended

2. **Agent Registration Process**
   - Initial registration based on hostname and capabilities
   - Subsequent authentication using assigned API key
   - Option for manual approval of new agents

## Network Security

### Server-Agent Communication

1. **HTTPS Encryption**
   - All traffic between agents and server should be encrypted
   - TLS 1.2+ recommended
   - Proper certificate validation

2. **Firewall Configuration**
   ```bash
   # Allow only necessary ports on management server
   sudo ufw allow 8082/tcp  # API server
   sudo ufw allow 8081/tcp  # Web dashboard
   
   # Restrict outgoing connections on agent nodes
   sudo iptables -A OUTPUT -p tcp -d MANAGEMENT_SERVER_IP --dport 8082 -j ACCEPT
   sudo iptables -A OUTPUT -p tcp -j DROP
   ```

3. **VPN Recommendations**
   - For public cloud deployments, use a VPN tunnel
   - WireGuard or OpenVPN recommended
   - Keep VPN credentials separate from application credentials

### Public-facing Deployments

For systems exposed to the internet:

1. **Reverse Proxy Configuration**
   ```nginx
   # Example Nginx configuration
   server {
       listen 443 ssl;
       server_name cracking.example.com;
       
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;
       
       location / {
           proxy_pass http://localhost:8081;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
       
       location /api {
           proxy_pass http://localhost:8082;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

2. **Rate Limiting**
   - Implement rate limiting for login attempts
   - Consider IP-based rate limiting for API endpoints
   - Use fail2ban or similar tools for automated blocking

3. **Web Application Firewall**
   - Consider deploying a WAF for additional protection
   - Block common attack patterns
   - Monitor for suspicious activity

## Data Security

### Sensitive Data Handling

1. **Password Hashes**
   - Store target password hashes securely
   - Implement access controls for hash databases
   - Consider encryption at rest

2. **Cracked Passwords**
   - Implement strict access controls for cracked results
   - Consider automatic redaction of sensitive information
   - Audit access to result data

3. **Database Security**
   - Use strong MongoDB authentication
   - Enable encryption at rest for production deployments
   - Regular security audits and updates

### File Security

1. **Temporary Files**
   - Securely handle temporary files containing sensitive data
   - Automatic cleanup after task completion
   - Use appropriate file permissions

2. **Wordlist Management**
   - Secure storage of wordlists and rules
   - Access control based on user role
   - Consider encryption for sensitive wordlists

## Operational Security

### Logging and Monitoring

1. **Security Logging**
   - Log all authentication attempts
   - Monitor for unusual patterns
   - Implement log rotation and retention policies

2. **Activity Auditing**
   - Track all user actions
   - Record task creation and assignment
   - Monitor agent registration and status changes

3. **Alerting**
   - Set up alerts for suspicious activities
   - Monitor for unauthorized access attempts
   - Track system resource usage

### Secure Deployment

1. **Container Security**
   - If using Docker, follow container security best practices
   - Use minimal base images
   - Regular security updates

2. **Principle of Least Privilege**
   - Run services with minimal required permissions
   - Separate user accounts for different components
   - Use systemd or similar for service management

3. **Regular Updates**
   - Keep all dependencies updated
   - Monitor for security advisories
   - Implement a patch management process

## Compliance Considerations

When using this system, be aware of potential legal and compliance issues:

1. **Authorized Testing Only**
   - Only use for authorized security testing
   - Obtain proper permissions before testing
   - Document authorization for all cracking tasks

2. **Data Protection Regulations**
   - Consider GDPR and similar regulations when handling personal data
   - Implement appropriate data retention policies
   - Provide mechanisms for data deletion when required

3. **Internal Policies**
   - Align usage with organizational security policies
   - Consider implementing approval workflows for sensitive operations
   - Maintain detailed audit trails
