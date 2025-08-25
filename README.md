# Natural Language to SQL Application

A Python application that converts natural language questions into SQL queries and executes them against a MySQL database.

## Features

- **Cacheable Schema Generation**: Generate database schema once and reuse
- **Natural Language Processing**: Convert questions to SQL using OpenAI
- **Safe Query Execution**: Execute queries with proper error handling
- **Interactive Mode**: Ask questions interactively
- **Command Line Interface**: Run single queries or manage schema

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
# OpenAI
OPENAI_API_KEY=your_openai_api_key

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

# Behavior
ROW_LIMIT=500
ALLOWED_SCHEMAS=
ALLOWED_TABLES=
```

## Usage

### Generate Schema Cache
```bash
python app.py generate-schema
```

### Interactive Mode
```bash
python app.py
```

### Single Question
```bash
python app.py "How many users are in the system?"
```

### Test Connection
```bash
python app.py test-connection
```

### Schema Information
```bash
python app.py schema-info
```

### Refresh Schema Cache
In interactive mode, type `refresh` to regenerate the schema cache.

## File Structure

- `app.py` - Main application entry point
- `config.py` - Configuration management
- `schema_cache.py` - Database schema caching system
- `database.py` - Database connection and query execution
- `ai_service.py` - OpenAI integration for SQL generation
- `schema_cache.json` - Generated schema cache file (auto-created)

## Commands

- `quit` / `exit` / `q` - Exit interactive mode
- `refresh` - Reload database schema
- `generate-schema` - Generate new schema cache
- `test-connection` - Test database connectivity
- `schema-info` - Show cached schema information