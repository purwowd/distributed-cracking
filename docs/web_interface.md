# Web Interface Documentation

The Distributed Hashcat Cracking system includes a web interface for monitoring and managing the distributed password cracking operations. This document provides information on how to use the web interface.

## Starting the Web Interface

There are several ways to start the web interface:

### Option 1: Using the start.py script (recommended)

The `start.py` script provides a convenient way to start all components of the system, including the web interface:

```bash
# Start all components (server, web interface, and one agent)
python start.py

# Start only the web interface
python start.py --web-only

# Start with custom web port
python start.py --web-port 9090

# Start in debug mode (enables auto-reload)
python start.py --debug

# Show output from all processes
python start.py --verbose
```

### Option 2: Directly running the web module

```bash
# From the project root
python -m cmd.web

# With custom host and port
python -m cmd.web --host 127.0.0.1 --port 9090

# With auto-reload for development
python -m cmd.web --reload
```

### Option 3: Running app.py directly

```bash
# From the project root
cd cmd/web
python app.py
```

## Web Interface Features

### Dashboard

The dashboard provides an overview of the system status, including:

- Task statistics (pending, running, completed, failed, cancelled)
- Agent statistics (online, busy, offline)
- Recent tasks with status and progress
- Recent cracked passwords

### Tasks

The Tasks page allows you to:

- View all tasks with their status and progress
- Create new tasks
- View task details
- Cancel or delete tasks

#### Creating a New Task

1. Click "New Task" on the Tasks page
2. Fill in the task details:
   - Name: A descriptive name for the task
   - Description: Optional description
   - Hash Type: Select the hash type from the dropdown
   - Hashes: Enter the hashes to crack (one per line)
   - Attack Mode: Select the attack mode (Dictionary, Rule-based, Mask, etc.)
   - Additional parameters based on the attack mode
3. Click "Create Task" to submit

### Agents

The Agents page shows all registered agents with their:

- Status (online, busy, offline)
- Hardware information (CPU, GPU)
- Current task (if any)
- Last seen timestamp

Clicking on an agent shows detailed information about its capabilities and configuration.

### Results

The Results page displays all cracked passwords with:

- Hash value
- Plaintext password
- Task that cracked it
- Timestamp

Features include:

- Filtering results by task, hash, or plaintext
- Copying hash or plaintext to clipboard
- Exporting results as CSV or TXT files

## Customizing the Web Interface

The web interface uses Bootstrap 5 for styling and can be customized by modifying:

- CSS: `cmd/web/static/css/custom.css`
- JavaScript: Files in `cmd/web/static/js/`
- Templates: Jinja2 templates in `cmd/web/templates/`

## Security Considerations

The current implementation does not include authentication or authorization. For production use, consider adding:

- User authentication
- Role-based access control
- HTTPS support
- Rate limiting

## Troubleshooting

Common issues:

1. **Web interface can't connect to the server**
   - Ensure the central server is running
   - Check that the API_URL in the configuration is correct

2. **Charts not displaying**
   - Ensure Chart.js is loaded correctly
   - Check browser console for JavaScript errors

3. **Static files not loading**
   - Verify that the static files are being served correctly
   - Check that file paths are correct in templates
