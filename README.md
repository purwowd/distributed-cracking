# Distributed Hashcat Cracking System

A distributed password cracking system using Hashcat with GPU acceleration, FastAPI, and MongoDB. The system consists of a central server that distributes cracking tasks to agent nodes with GPU capabilities. Supports various hash types, attack modes, and provides both web interface and RESTful API with secure user authentication.

## Features

- **Distributed Processing**: Efficiently distribute cracking tasks across multiple agents
- **GPU Acceleration**: Utilize Hashcat's GPU acceleration for maximum performance
- **Multiple Attack Modes**: Support for dictionary, mask, rule-based, and hybrid attacks
- **Real-time Monitoring**: Track task progress and agent status in real-time
- **Robust API**: RESTful API with pagination, filtering, and detailed documentation
- **Authentication**: JWT-based authentication with role-based access control
- **Exception Handling**: Comprehensive error handling and logging
- **Clean Architecture**: Well-organized codebase with clear separation of concerns

## Architecture

The system is built using Clean Architecture principles with clear separation of concerns:

### System Components
- **Central Server**: Manages tasks, distributes work, and collects results
- **Agent Nodes**: GPU-equipped servers running Hashcat for password cracking
- **MongoDB**: Stores tasks, results, and system configuration
- **Web Interface**: Bootstrap-based dashboard for monitoring and management
- **CLI Tool**: Command-line interface for system management

### Clean Architecture Layers
- **Entity Layer**: Core domain objects (Task, Agent, Result)
- **Repository Layer**: Data access for MongoDB with specific exceptions
- **Model Layer**: Pydantic models for API requests/responses with pagination
- **Usecase Layer**: Business logic implementation with error handling
- **Exception Layer**: Custom exceptions for different layers
- **Config Layer**: System configuration, authentication, and logging
- **Command Layer**: Entry points (server.py, agent.py, cli.py, web/app.py)

### Key Architectural Features

#### Pagination with Metadata
All list endpoints support pagination with comprehensive metadata including:
- Total count of items
- Skip and limit parameters
- Has more indicator
- Current page information

#### Exception Handling
Robust exception handling with layer-specific exceptions:
- **Repository Exceptions**: EntityNotFoundException, DuplicateEntityException, DatabaseOperationException
- **Usecase Exceptions**: ResourceNotFoundException, ResourceConflictException, BusinessRuleViolationException, InvalidOperationException, AuthorizationException

#### Authentication and Authorization
- JWT-based authentication with OAuth2 password flow
- Role-based access control for admin operations
- Secure password hashing with bcrypt
- Configurable token expiration

## Project Structure

```
distributed-cracking/
├── cmd/                # Command-line entry points
│   ├── server.py       # Central server implementation
│   ├── agent.py        # Agent node implementation
│   ├── cli.py          # Command-line interface
│   └── web/            # Web dashboard
│       ├── static/     # Static assets (CSS, JS)
│       └── templates/  # Jinja2 HTML templates
├── config/             # Configuration management
│   ├── auth.py         # Authentication and JWT handling
│   ├── api_docs.py     # API documentation configuration
│   └── logging_config.py # Logging configuration
├── entity/             # Core domain entities
│   ├── task.py         # Task entity
│   ├── agent.py        # Agent entity
│   └── result.py       # Result entity
├── model/              # Data models and schemas
│   ├── task.py         # Task request/response models
│   ├── agent.py        # Agent request/response models
│   ├── result.py       # Result request/response models
│   ├── pagination.py   # Pagination models
│   └── examples.py     # API examples for documentation
├── repository/         # Data access layer
│   ├── task_repository.py    # Task data access
│   ├── agent_repository.py   # Agent data access
│   └── result_repository.py  # Result data access
├── usecase/            # Business logic and use cases
│   ├── task_usecase.py       # Task business logic
│   ├── agent_usecase.py      # Agent business logic
│   └── result_usecase.py     # Result business logic
├── exception/          # Custom exceptions
│   ├── repository_exception.py  # Repository layer exceptions
│   └── usecase_exception.py     # Usecase layer exceptions
└── test/               # Test suite
```

## Authentication & Login System

The system includes a secure authentication system with the following features:

- **JWT-based Authentication**: Secure JSON Web Tokens with configurable expiration
- **Role-based Access Control**: Different permission levels for admin and regular users
- **Bcrypt Password Hashing**: Secure password storage with modern hashing algorithm
- **Login Session Management**: Persistent login sessions with HTTP-only cookies
- **Protected Routes**: Automatic redirection to login page for unauthenticated access attempts

### Default Login Credentials

When using the mock database (development mode), the following credentials are available:

| Username | Password | Role  |
|----------|----------|-------|
| admin    | password | ADMIN |
| user     | password | USER  |

## Database Configuration

The system supports both a mock database for development and MongoDB for production:

### Mock Database (Development Mode)

By default, the system uses a mock database for easy development and testing:

```
# In .env file
USE_MOCK_DATABASE=true
```

The mock database provides pre-configured users, tasks, agents, and results for testing purposes without requiring a MongoDB installation.

### MongoDB (Production Mode)

For production use, configure the system to use MongoDB:

```
# In .env file
USE_MOCK_DATABASE=false
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=hashcat_cracking
```

When switching from mock to MongoDB, ensure that:
1. MongoDB is installed and running on the specified URI
2. Initial user accounts are created in the MongoDB database
3. Required collections are initialized

### MongoDB Setup Scripts

The system includes utility scripts to help you set up MongoDB and manage users:

#### Initialize MongoDB

To initialize MongoDB with required collections, indexes, and default users:

```bash
# Basic initialization with default users (admin/password and user/password)
python scripts/init_mongodb.py

# Initialize with sample data (optional)
python scripts/init_mongodb.py --with-sample-data
```

This script will:
- Create all necessary collections (users, tasks, agents, results, files)
- Set up required indexes for optimal performance
- Create default admin and regular user accounts with the same credentials as the mock database

#### Create New Users

To create additional users in MongoDB:

```bash
# Format: python scripts/create_user.py <username> <email> <password> <role>
python scripts/create_user.py admin2 admin2@example.com secure_password admin
python scripts/create_user.py operator operator@example.com secure_password user
```

Available roles: `admin`, `user`, `viewer`

### Migrating from Mock Database to MongoDB

Follow these steps to migrate from development mode (mock database) to production mode (MongoDB):

1. **Install and Start MongoDB**
   ```bash
   # For macOS with Homebrew
   brew install mongodb-community
   brew services start mongodb-community
   
   # For Ubuntu/Debian
   sudo apt install mongodb
   sudo systemctl start mongodb
   ```

2. **Initialize MongoDB with Required Structure**
   ```bash
   python scripts/init_mongodb.py
   ```

3. **Update Environment Configuration**
   ```bash
   # Edit .env file to change USE_MOCK_DATABASE to false
   sed -i '' 's/USE_MOCK_DATABASE=true/USE_MOCK_DATABASE=false/g' .env
   ```

4. **Verify MongoDB Connection**
   ```bash
   # Start the application and verify it connects to MongoDB
   python -m cmd.web
   ```

5. **Optional: Import Existing Data**
   If you have important data in your mock database that you want to preserve, you can create a custom migration script based on your specific needs.

## Quick Start

The easiest way to start all components is to use the start script:

```bash
# Start all components (server, web interface, and one agent)
python start.py

# Start with more options
python start.py --agents 2 --web-port 9090 --debug --verbose
```

For more control, you can start components individually:

```bash
# Start only the central server
python start.py --server-only

# Start only the web interface
python start.py --web-only

# Start only the agents
python start.py --agents-only --agents 3
```

## Installation

### Requirements

- Python 3.8 or higher
- MongoDB (for production mode) or use built-in mock database for development
- Hashcat with GPU support (for agent nodes)
- CUDA or OpenCL drivers (for GPU acceleration)

### Dependencies

The system requires the following Python packages:

- FastAPI: Web framework for API and dashboard
- Uvicorn: ASGI server for FastAPI
- Jinja2: Template engine for web dashboard
- PyMongo/Motor: MongoDB async driver
- Pydantic: Data validation and settings management
- Python-Jose: JWT token handling
- Passlib: Password hashing with bcrypt
- Requests: HTTP client for agent communication
- Pytest: For running tests

### Manual Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/distributed-cracking.git
   cd distributed-cracking
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env` file:
   ```bash
   # Copy example env file
   cp .env.example .env
   # Edit as needed
   nano .env
   ```

4. Start the central server:
   ```bash
   python -m cmd.server
   ```

5. Deploy agents on GPU servers:
   ```bash
   python -m cmd.agent
   ```

6. Start the web dashboard:
   ```bash
   python -m cmd.web
   ```

## Web Interface

The web interface provides a user-friendly dashboard for managing the distributed cracking system:

- **Dashboard**: Overview of system statistics, recent tasks, and results
  - Real-time performance metrics and charts
  - System status indicators and agent availability
  - Recent task completion statistics

- **Tasks**: Create, view, manage, and monitor cracking tasks
  - Create standard tasks with custom parameters
  - Create specialized WPA/WPA2 cracking tasks
  - Filter tasks by status, hash type, and other parameters
  - Real-time progress monitoring

- **Agents**: Monitor agent status, capabilities, and hardware information
  - View agent hardware specifications
  - Monitor agent availability and workload
  - Assign tasks to specific agents

- **Results**: View and export cracked passwords
  - Filter results by task, hash value, or plaintext
  - Export results in various formats
  - Secure viewing of sensitive password data

- **File Management**: Upload and manage handshake files and wordlists
  - Support for .hccapx files for WPA/WPA2 cracking
  - Custom wordlist uploads and default wordlist selection
  - Secure file deletion and management
  - Integration with WPA task creation workflow

- **User Profile**: Manage user settings and security
  - View account information
  - Change password
  - View activity history

### Secure Authentication

The web interface features a secure login system with:

- Modern, responsive login page
- Persistent sessions across all pages
- Consistent navbar showing login status
- User profile dropdown with role indication
- Automatic redirection to login for protected pages

Access the web interface at `http://localhost:8082` (or the configured SERVER_PORT in .env).

## Command-Line Interface

The CLI tool provides command-line access to manage the system:

```
python -m cmd.cli tasks list
python -m cmd.cli tasks create --name "Example Task" --hash-type "md5" --hashes-file "hashes.txt"
python -m cmd.cli agents list
python -m cmd.cli results search --hash "5f4dcc3b5aa765d61d8327deb882cf99"
```

## RESTful API

The system provides a comprehensive RESTful API for integration with other applications. All API endpoints include detailed documentation, request/response examples, and support for pagination with metadata.

### Authentication Endpoints
- `POST /token` - Authenticate user and get JWT access token
- `GET /users/me` - Get current authenticated user information

### Task API Endpoints
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks with pagination and optional filtering
- `GET /tasks/{task_id}` - Get task details by ID
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task (admin only)
- `POST /tasks/{task_id}/cancel` - Cancel a running task
- `POST /tasks/{task_id}/assign/{agent_id}` - Manually assign task to agent

### Agent API Endpoints
- `POST /agents` - Register a new agent (admin only)
- `GET /agents` - List all agents with pagination and optional filtering
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent (admin only)
- `POST /agents/heartbeat` - Update agent heartbeat with resource usage

### Result API Endpoints
- `GET /results` - List all results with pagination and optional filtering
- `GET /results/{result_id}` - Get result details
- `DELETE /results/{result_id}` - Delete result (admin only)

API documentation is available at `/docs` when the server is running.

## Deployment Options

The system can be deployed in various configurations:

- **Single Machine**: Run server and agent on the same machine (development setup)
- **Local Network**: Management server with multiple agents on the same network
- **Hybrid Cloud**: Combine local and cloud-based agents
- **Multi-GPU Types**: Mix AMD and NVIDIA GPUs across different nodes

### Multi-Node Deployment

The system supports distributed deployment across multiple nodes with different GPU types:

```bash
# On management server (Mini PC with AMD GPU)
python -m cmd.server  # Start central server
python -m cmd.web     # Start web dashboard
python -m cmd.agent --server-url http://localhost:8082 --name "local-amd-node"  # Local agent

# On remote node (Cloud server with NVIDIA GPU)
python -m cmd.agent --server-url http://YOUR_MINI_PC_IP:8082 --name "cloud-nvidia-node"
```

For detailed deployment instructions, including:
- Setting up local and cloud nodes
- Connecting to public cloud GPU servers
- Network and security configuration
- Example configuration files

See [docs/deployment.md](docs/deployment.md)

## Security Considerations

The system includes several security features:

- **Authentication**: JWT-based authentication with HTTP-only cookies
- **Password Security**: Bcrypt hashing with appropriate work factor
- **Role-based Access Control**: Admin, user, and viewer roles with appropriate permissions
- **API Security**: API key authentication for agent-server communication

For comprehensive security guidelines, including:
- Network security configuration
- HTTPS setup
- Secure deployment practices
- Data protection measures
- Operational security recommendations

See [docs/security.md](docs/security.md)

## Troubleshooting

### Authentication Issues

- **Login Failures**: Ensure you're using the correct credentials. Default mock database credentials are `admin`/`password` or `user`/`password`.
- **Session Not Persisting**: Check that cookies are enabled in your browser and that the JWT token is being properly stored.
- **Permission Denied**: Certain operations require admin privileges. Ensure you're logged in with an admin account.

### Database Configuration

- **Mock Database Issues**: If using the mock database (`USE_MOCK_DATABASE=true`), ensure the application has read/write permissions to the directory.
- **MongoDB Connection Errors**: When switching to MongoDB (`USE_MOCK_DATABASE=false`):
  - Verify MongoDB is running on the configured URI
  - Check network connectivity and firewall settings
  - Ensure the database user has appropriate permissions

### Common Errors

- **Hashcat Not Found**: Ensure the `HASHCAT_PATH` in `.env` points to a valid hashcat installation.
- **File Upload Errors**: Check that the upload directories exist and have proper permissions.
- **Agent Communication Failures**: Verify network connectivity between server and agent nodes.

## Security Considerations

### Production Deployment

When deploying to production, consider the following security measures:

1. **HTTPS**: Always use HTTPS in production with a valid SSL certificate.
2. **Environment Variables**: Store sensitive information like JWT secrets in environment variables, not in code.
3. **Rate Limiting**: Implement rate limiting on login endpoints to prevent brute force attacks.
4. **Firewall Rules**: Restrict access to the server and agent nodes using firewall rules.
5. **Regular Updates**: Keep all dependencies updated to patch security vulnerabilities.
6. **Secure Password Storage**: The system uses bcrypt for password hashing, but ensure password complexity requirements are enforced.
7. **Access Control**: Implement proper role-based access control for all sensitive operations.
8. **Audit Logging**: Enable comprehensive logging for security-relevant events.

### Sensitive Data Handling

The system processes password hashes and plaintext passwords, which are sensitive data:

1. **Data Encryption**: Consider encrypting sensitive data at rest.
2. **Data Retention**: Implement policies for secure deletion of sensitive data when no longer needed.
3. **Access Logs**: Monitor and audit access to sensitive data.
4. **Data Minimization**: Only collect and store the minimum necessary data.

## Supported Hash Types

The system supports all hash types available in Hashcat, including but not limited to:

- **Hash Algorithms**: MD5, SHA1, SHA256, SHA512, NTLM, etc.
- **Application Hashes**: WordPress, phpBB, Joomla, etc.
- **Encrypted Files**: Office documents, PDF, ZIP, RAR, etc.
- **Network Protocols**: WPA/WPA2, WPA-PMKID, RADIUS, VPN, etc.
- **Database Hashes**: MySQL, PostgreSQL, Oracle, MSSQL, etc.
- **Cryptocurrency**: Bitcoin wallet, Ethereum wallet, etc.

## Attack Modes

- **Dictionary Attack (Mode 0)**: Using wordlists
- **Combination Attack (Mode 1)**: Combining two wordlists
- **Mask Attack (Mode 3)**: Using character patterns
- **Hybrid Attack (Mode 6 & 7)**: Combining wordlists and masks
- **Rule-based Attack**: Applying transformation rules to wordlists

## Database Configuration

The system can use either a mock database (for development) or MongoDB (for production):

### Mock Database
- Enabled by default for easy development and testing
- Data stored in memory, not persisted between restarts
- Set `USE_MOCK_DATABASE=true` in `.env` file
- Default credentials: username `admin` or `user`, password `password`

### MongoDB
- Recommended for production use
- Persistent storage with better performance and scalability
- Set `USE_MOCK_DATABASE=false` in `.env` file
- Configure connection with `MONGODB_URI` and `DATABASE_NAME` in `.env`

For detailed MongoDB setup instructions, including:
- Installation and configuration
- Database initialization
- User management
- Performance optimization
- Backup and recovery

See [docs/mongodb.md](docs/mongodb.md)

## Requirements

- Python 3.8+
- MongoDB (optional, can use mock database for development)
- Hashcat installed on agent nodes
- CUDA-compatible GPUs on agent nodes

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- [Hashcat](https://hashcat.net/) - Advanced password recovery utility
- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework for building APIs
- [MongoDB](https://www.mongodb.com/) - NoSQL database
- [Bootstrap](https://getbootstrap.com/) - Front-end framework