# Web Interface for Distributed Hashcat Cracking

This directory contains the web interface for the Distributed Hashcat Cracking system. The web interface provides a user-friendly dashboard for monitoring and managing the distributed password cracking system.

## Structure

```
web/
├── app.py                # FastAPI web application entry point
├── static/              # Static assets
│   ├── css/             # CSS stylesheets
│   │   └── custom.css   # Custom styles for the web interface
│   └── js/              # JavaScript files
│       ├── dashboard-charts.js  # Chart.js initialization for dashboard
│       └── results.js           # Results page functionality
└── templates/           # Jinja2 HTML templates
    ├── base.html        # Base template with common layout
    ├── dashboard.html   # Dashboard overview
    ├── tasks.html       # Task listing
    ├── task_detail.html # Task details
    ├── task_new.html    # New task form
    ├── agents.html      # Agent listing
    ├── agent_detail.html # Agent details
    └── results.html     # Results listing
```

## Features

- **Dashboard**: Overview of system statistics, recent tasks, and results
- **Tasks Management**: Create, view, manage, and monitor cracking tasks
- **Agents Monitoring**: Monitor agent status, capabilities, and hardware information
- **Results Viewing**: View and export cracked passwords

## Technologies Used

- **FastAPI**: Web framework for the backend
- **Jinja2**: HTML templating engine
- **Bootstrap 5**: CSS framework for responsive design
- **Chart.js**: JavaScript library for charts and graphs
- **Bootstrap Icons**: Icon library

## Running the Web Interface

```bash
# From the project root
python -m cmd.web.app
```

The web interface will be available at `http://localhost:8080` by default.

## Extending the Web Interface

### Adding New Pages

1. Create a new Jinja2 template in the `templates` directory
2. Add a new route in `app.py`
3. Update the navigation in `base.html`

### Adding New JavaScript Functionality

1. Create a new JavaScript file in the `static/js` directory
2. Include it in the appropriate template using the `extra_js` block:

```html
{% block extra_js %}
<script src="/static/js/your-script.js"></script>
{% endblock %}
```

### Adding New Styles

1. Add your styles to `static/css/custom.css`
2. For page-specific styles, use the `extra_css` block:

```html
{% block extra_css %}
<style>
    /* Your page-specific styles here */
</style>
{% endblock %}
```

## Security Considerations

- The web interface currently does not implement authentication
- Consider adding authentication for production use
- API keys for agents are managed separately from the web interface
