# Distributed Hashcat Cracking System

A distributed password cracking system using Hashcat with GPU acceleration, FastAPI, and MongoDB. The system consists of a central server that distributes cracking tasks to agent nodes with GPU capabilities. Supports various hash types, attack modes, and provides both web interface and RESTful API.

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
- **Repository Layer**: Data access for MongoDB (TaskRepository, AgentRepository, ResultRepository)
- **Model Layer**: Pydantic models for API requests/responses
- **Usecase Layer**: Business logic implementation
- **Config Layer**: System configuration and database connection
- **Command Layer**: Entry points (server.py, agent.py, cli.py, web/app.py)

## Project Structure

```
distributed-cracking/
├── cmd/                # Command-line entry points
│   ├── web/            # Web dashboard
│   │   ├── static/     # Static assets (CSS, JS)
│   │   └── templates/  # Jinja2 HTML templates
│   ├── server/         # Central server implementation
│   └── agent/          # Agent node implementation
├── config/             # Configuration management
├── docs/               # Documentation
├── entity/             # Core domain entities
├── model/              # Data models and schemas
├── repository/         # Data access layer
├── usecase/            # Business logic and use cases
└── test/               # Test suite
```

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

## Manual Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`

3. Start the central server:
   ```
   python -m cmd.server
   ```

4. Deploy agents on GPU servers:
   ```
   python -m cmd.agent
   ```

5. Start the web dashboard:
   ```
   python -m cmd.web
   ```

## Web Interface

The web interface provides a user-friendly dashboard for managing the distributed cracking system:

- **Dashboard**: Overview of system statistics, recent tasks, and results
- **Tasks**: Create, view, manage, and monitor cracking tasks
  - Create standard tasks with custom parameters
  - Create specialized WPA/WPA2 cracking tasks
  - Filter tasks by status, hash type, and other parameters
- **Agents**: Monitor agent status, capabilities, and hardware information
- **Results**: View and export cracked passwords
  - Filter results by task, hash value, or plaintext
- **File Management**: Upload and manage handshake files and wordlists
  - Support for .hccapx files for WPA/WPA2 cracking
  - Custom wordlist uploads and default wordlist selection
  - Secure file deletion and management
  - Integration with WPA task creation workflow

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

The system provides a comprehensive RESTful API for integration with other applications:

### Task API Endpoints
- `POST /tasks` - Create a new task
- `GET /tasks` - List all tasks with optional filtering
- `GET /tasks/{task_id}` - Get task details by ID
- `PUT /tasks/{task_id}` - Update task
- `DELETE /tasks/{task_id}` - Delete task
- `POST /tasks/{task_id}/cancel` - Cancel a running task

### Agent API Endpoints
- `POST /agents` - Register a new agent
- `GET /agents` - List all agents
- `GET /agents/{agent_id}` - Get agent details
- `PUT /agents/{agent_id}` - Update agent
- `DELETE /agents/{agent_id}` - Delete agent
- `POST /agents/heartbeat` - Send agent heartbeat

### Result API Endpoints
- `GET /results` - List all results with optional filtering
- `GET /results/{result_id}` - Get result details
- `GET /results/hash/{hash_value}` - Find result by hash value

API documentation is available at `/docs` (Swagger UI) or `/redoc` (ReDoc) when the server is running.

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

### MongoDB
- Recommended for production use
- Persistent storage with better performance and scalability
- Set `USE_MOCK_DATABASE=false` in `.env` file
- Configure connection with `MONGODB_URI` and `DATABASE_NAME` in `.env`

See `README_MONGODB.md` for detailed MongoDB setup instructions.

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