# Apache Guacamole Docker Compose Setup

A complete Docker Compose setup for running Apache Guacamole with MySQL database backend. This project provides a production-ready Guacamole instance with automated database initialization and user management.

## 🚀 Features

- **Apache Guacamole**: Web-based remote desktop gateway
- **MySQL Database**: Persistent data storage with automated setup
- **Docker Compose**: Easy deployment and management
- **Automated Database Setup**: Custom initialization scripts
- **Network Isolation**: Secure container networking
- **Persistent Storage**: Database data persistence across restarts

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- At least 2GB RAM available
- Port 8080 available on your host

## 🏗️ Architecture

The setup consists of four main services:

- **`guacd`**: Guacamole daemon (remote desktop proxy)
- **`guacweb`**: Guacamole web application
- **`guacamole-sql`**: MySQL database server
- **`db-setup`**: Database initialization service

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd Guacamole
```

### 2. Start the Services

```bash
# Start all services in detached mode
docker-compose up -d --build

# Or start with logs visible
docker-compose up --build
```

### 3. Access Guacamole

Open your browser and navigate to:
```
http://localhost:8080/guacamole/
```

### 4. Default Login Credentials

- **Username**: `guacadmin`
- **Password**: `guacadmin`

⚠️ **Important**: Change these default credentials after first login!

## 🔧 Configuration

### Environment Variables

The main configuration is handled through Docker Compose environment variables:

- `MYSQL_DATABASE`: Database name (default: `guacamole_db`)
- `MYSQL_HOSTNAME`: Database host (default: `guacamole-sql`)
- `MYSQL_USER`: Database user (default: `guacamole_user`)
- `MYSQL_PASSWORD`: Database password (default: `pass`)
- `GUACD_HOSTNAME`: Guacamole daemon host (default: `guacd`)

### Port Configuration

- **8080**: Guacamole web interface
- **3306**: MySQL database (internal only)

### Volumes

- `./dbdata`: MySQL data persistence
- `./sql_scripts`: Database initialization scripts

## 📁 Project Structure

```
Guacamole/
├── docker-compose.yml          # Main Docker Compose configuration
├── docker-compose-first-run.yml # First-time setup configuration
├── Dockerfile                  # Base image for database setup
├── create_db.sh               # Database creation script
├── sql_scripts/               # SQL scripts and database setup
│   ├── Dockerfile            # Database setup container
│   ├── create_db.sh          # Database initialization
│   ├── initdb.sql            # Database schema
│   ├── cleandb.sql           # Database cleanup script
│   └── *.sql                 # Additional SQL scripts
└── dbdata/                    # MySQL data directory (auto-created)
```

## 🗄️ Database Management

### Initial Setup

The database is automatically initialized on first run through the `db-setup` service, which:

1. Creates the `guacamole_db` database
2. Creates the `guacamole_user` with appropriate permissions
3. Imports the initial schema from `initdb.sql`

### Manual Database Operations

If you need to run database operations manually:

```bash
# Connect to MySQL container
docker exec -it guac-sql mysql -uroot -ppass

# Or run a specific SQL script
docker exec -i guac-sql mysql -uroot -ppass guacamole_db < script.sql
```

## 🛠️ Maintenance

### Viewing Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs guacweb
docker-compose logs guacd
docker-compose logs guacamole-sql
```

### Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ WARNING: This will delete all data!)
docker-compose down -v
```

### Updating

```bash
# Pull latest images and rebuild
docker-compose pull
docker-compose up -d --build
```

## 🔒 Security Considerations

- Change default passwords immediately after first login
- Consider using environment files for sensitive data
- Database is only accessible from within the Docker network
- Use HTTPS in production environments

## 🐛 Troubleshooting

### Common Issues

1. **Port 8080 already in use**
   ```bash
   # Check what's using the port
   sudo netstat -tulpn | grep :8080
   # Change port in docker-compose.yml if needed
   ```

2. **Database connection errors**
   ```bash
   # Check if database is running
   docker-compose ps guacamole-sql
   # Check database logs
   docker-compose logs guacamole-sql
   ```

3. **Permission denied errors**
   ```bash
   # Ensure proper file permissions
   chmod +x sql_scripts/*.sh
   ```

### Reset Everything

```bash
# Complete reset (⚠️ WARNING: All data will be lost!)
docker-compose down -v
rm -rf dbdata/
docker-compose up -d --build
```

## 📚 Additional Resources

- [Apache Guacamole Documentation](https://guacamole.apache.org/doc/gug/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [MySQL Docker Image](https://hub.docker.com/_/mysql)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the same license as Apache Guacamole.

## ⚠️ Disclaimer

This setup is provided as-is for educational and development purposes. For production use, ensure proper security hardening, backup strategies, and monitoring are in place.

