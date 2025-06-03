# MongoDB Configuration Guide

This guide provides detailed instructions for setting up, configuring, and optimizing MongoDB for the Distributed Hashcat Cracking System.

## MongoDB Setup

### Installation

#### Ubuntu/Debian
```bash
# Import MongoDB public GPG key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Create list file for MongoDB
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Update package database
sudo apt-get update

# Install MongoDB
sudo apt-get install -y mongodb-org

# Start MongoDB service
sudo systemctl start mongod

# Enable MongoDB to start on boot
sudo systemctl enable mongod
```

#### macOS
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB service
brew services start mongodb-community
```

### Verifying Installation
```bash
# Check MongoDB status
mongosh --eval "db.runCommand({ connectionStatus: 1 })"
```

## Database Initialization

### Using the Initialization Script

The system includes a script to initialize MongoDB with the required collections, indexes, and default users:

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

### Manual Collection Setup

If you prefer to set up collections manually:

```javascript
// Connect to MongoDB shell
mongosh

// Create database
use hashcat_cracking

// Create collections with validators
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["username", "hashed_password", "role", "created_at"],
      properties: {
        username: { bsonType: "string" },
        email: { bsonType: "string" },
        hashed_password: { bsonType: "string" },
        role: { bsonType: "string" },
        created_at: { bsonType: "date" },
        last_login: { bsonType: "date" }
      }
    }
  }
})

// Create indexes
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true, sparse: true })

// Similar setup for other collections (tasks, agents, results, files)
```

## User Management

### Creating Users with the Script

To create additional users in MongoDB:

```bash
# Format: python scripts/create_user.py <username> <email> <password> <role>
python scripts/create_user.py admin2 admin2@example.com secure_password admin
python scripts/create_user.py operator operator@example.com secure_password user
```

Available roles: `admin`, `user`, `viewer`

### Manual User Creation

To manually create a user with bcrypt password hashing:

```python
import bcrypt
import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["hashcat_cracking"]
users = db["users"]

# Create user with hashed password
hashed_password = bcrypt.hashpw("secure_password".encode(), bcrypt.gensalt(rounds=12)).decode()
user = {
    "username": "new_admin",
    "email": "admin@example.com",
    "hashed_password": hashed_password,
    "role": "admin",
    "created_at": datetime.utcnow()
}
users.insert_one(user)
```

## Migrating from Mock Database

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

## Performance Optimization

### Index Optimization

The initialization script creates the following indexes for optimal performance:

1. **Users Collection**
   - `username`: Unique index for fast lookups during authentication
   - `email`: Unique index for user identification

2. **Tasks Collection**
   - `status`: For filtering tasks by status
   - `created_at`: For sorting and filtering by creation date
   - `assigned_agent_id`: For finding tasks assigned to specific agents

3. **Agents Collection**
   - `hostname`: For identifying agents
   - `status`: For filtering by agent status

4. **Results Collection**
   - `task_id`: For finding results associated with specific tasks
   - `created_at`: For sorting and filtering by creation date

### Connection Pooling

The system uses connection pooling for optimal performance. You can adjust the pool size in `config/database.py`:

```python
client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=50,
    minPoolSize=10
)
```

### Recommended MongoDB Configuration

For production deployments, consider the following MongoDB configuration options:

```yaml
# mongod.conf
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 2  # Adjust based on available RAM

operationProfiling:
  slowOpThresholdMs: 100
  mode: slowOp

net:
  bindIp: 127.0.0.1  # Restrict to localhost unless remote access is needed
  port: 27017
```

## Backup and Recovery

### Regular Backups

Set up regular backups using `mongodump`:

```bash
# Create a backup script
cat > backup_mongodb.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/path/to/backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR
mongodump --db hashcat_cracking --out $BACKUP_DIR
# Optionally compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR
# Keep only last 7 backups
find /path/to/backups -name "*.tar.gz" -type f -mtime +7 -delete
EOF

# Make it executable
chmod +x backup_mongodb.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/backup_mongodb.sh") | crontab -
```

### Restoration

To restore from a backup:

```bash
# Extract backup if compressed
tar -xzf backup_file.tar.gz

# Restore database
mongorestore --db hashcat_cracking backup_directory/hashcat_cracking
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if MongoDB service is running: `systemctl status mongod`
   - Verify MongoDB is listening on the expected port: `netstat -tuln | grep 27017`

2. **Authentication Failed**
   - Verify MongoDB is running without authentication mode for initial setup
   - Check username and password in connection string

3. **Slow Queries**
   - Check for missing indexes: `db.collection.find().explain()`
   - Monitor MongoDB performance: `mongostat`

### Logging

Enable detailed logging for troubleshooting:

```yaml
# mongod.conf
systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  verbosity: 1  # Increase to 2 for more detailed logs
```

## Security Recommendations

See [security.md](security.md) for comprehensive security guidelines, including:

1. **Authentication**: Enable MongoDB authentication
2. **Encryption**: Configure encryption at rest
3. **Network Security**: Restrict MongoDB access to localhost or VPN
4. **Regular Updates**: Keep MongoDB updated with security patches
