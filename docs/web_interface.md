# Web Interface Documentation

The Distributed Hashcat Cracking system includes a web interface for monitoring and managing the distributed password cracking operations. This document provides information on how to use the web interface.

## Starting the Web Interface

There are several ways to start the web interface:

### Option 1: Using environment variables

Configure the web interface using environment variables in your `.env` file:

```
# Web interface settings
WEB_HOST=0.0.0.0  # Listen on all interfaces
WEB_PORT=8081     # Default web port
```

Then start the web interface:

```bash
# From the project root
python -m cmd.web
```

### Option 2: Using command-line arguments

```bash
# From the project root
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

## Login System

The system includes a secure authentication system:

### Default Credentials

When using the mock database (development mode), the following credentials are available:

| Username | Password | Role  |
|----------|----------|-------|
| admin    | password | ADMIN |
| user     | password | USER  |

### Login Flow

1. Accessing any protected page redirects unauthenticated users to the login page
2. After successful login, users are redirected to the dashboard
3. The logout button redirects users back to the login page

### Authentication Features

- JWT tokens stored in HTTP-only cookies
- Role-based access control (admin, user, viewer)
- Bcrypt password hashing
- Configurable token expiration

### Database Compatibility

The login system works with both:
- Mock database (development mode)
- MongoDB (production mode)

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

The system includes authentication and authorization features:

- **JWT-based Authentication**: Secure login with HTTP-only cookies
- **Role-based Access Control**: Different permission levels (admin, user, viewer)
- **Password Security**: Bcrypt hashing for secure password storage

For additional security in production environments:

- Enable HTTPS with valid certificates
- Implement rate limiting for login attempts
- Consider IP-based access restrictions
- Set up proper firewall rules

See [security.md](security.md) for comprehensive security guidelines.

## Troubleshooting

Common issues:

1. **Authentication Issues**
   - **Login Failures**: Ensure you're using the correct credentials. Default mock database credentials are `admin`/`password` or `user`/`password`.
   - **Session Not Persisting**: Check that cookies are enabled in your browser and that the JWT token is being properly stored.
   - **Permission Denied**: Certain operations require admin privileges. Ensure you're logged in with an admin account.

2. **Web interface can't connect to the server**
   - Ensure the central server is running (`python -m cmd.server`)
   - Check that the API_URL in the configuration is correct
   - Verify network connectivity between web interface and server
   - For multi-node setups, ensure proper network configuration

3. **Agent Connection Issues**
   - Verify agents are properly registered and connected
   - Check agent logs for connection errors
   - For cloud agents, ensure proper network configuration as described in [deployment.md](deployment.md)

4. **Charts not displaying**
   - Ensure Chart.js is loaded correctly
   - Check browser console for JavaScript errors

5. **Static files not loading**
   - Verify that the static files are being served correctly
   - Check that file paths are correct in templates

6. **Database Connection Issues**
   - If using MongoDB, verify the database is running and accessible
   - Check connection string in `.env` file
   - See [mongodb.md](mongodb.md) for detailed MongoDB troubleshooting
