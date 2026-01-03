# TinyURL Backend

A distributed URL shortening service using FastAPI, Cassandra, and Nginx load balancing.

## System Design Architecture

```
                    ┌─────────────────────┐
                    │   Client Request    │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Nginx Load        │
                    │  Balancer          │
                    │  (Port 8090)       │
                    └──────────┬──────────┘
                    ┌──────────┴──────────┐
         ┌──────────▼──────────┐  ┌──────────▼──────────┐
         │   FastAPI App 1     │  │   FastAPI App 2     │
         │   (Port 8001)       │  │   (Port 8002)       │
         │  Uvicorn Server     │  │  Uvicorn Server     │
         └──────────┬──────────┘  └──────────┬──────────┘
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Cassandra DB     │
                    │   (Port 9042)      │
                    │ Distributed Store  │
                    └────────────────────┘
```

**Key Components:**
- **Load Balancer**: Nginx distributes traffic across multiple app instances
- **API Servers**: Stateless FastAPI instances process requests independently
- **Database**: Cassandra provides distributed, scalable data persistence

## Quick Start

### Using Docker Compose
```bash
docker-compose up --build
```

Access the services:
- **Load Balancer**: http://localhost:8090
- **App Instance 1**: http://localhost:8001
- **App Instance 2**: http://localhost:8002

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/healthcheck` | Service health status |
| `GET` | `/` | Service info & hostname |
| `POST` | `/shorten` | Create short URL |
| `GET` | `/{short_code}` | Redirect to long URL |

### Shorten URL
```bash
POST /shorten?long_url=https://example.com&expiry_days=30

Response:
{
  "short_url": "http://localhost:8000/abc123xyz"
}
```

### Redirect
```bash
GET /{short_code}
→ 302 Redirect to original URL (or 404 if expired)
```

## Database Setup

**Keyspace:**
```sql
CREATE KEYSPACE tinyurl WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
```

**Table:**
```sql
CREATE TABLE tinyurl.short_urls (
    short_code TEXT PRIMARY KEY,
    long_url TEXT,
    created_at TIMESTAMP
);
```

## Project Structure

```
tinyurl_backend/
├── main.py              # FastAPI app & endpoints
├── cassandra_client.py  # DB connection
├── utils.py             # Helper functions
├── requirements.txt     # Dependencies
├── Dockerfile           # Container image
├── docker-compose.yml   # Service orchestration
├── nginx/
│   └── nginx.conf       # Load balancer config
└── README.md
```

## Dependencies

```
fastapi          - Web framework
uvicorn          - ASGI server
cassandra-driver - DB client
validators       - URL validation
```

## Features

✅ URL shortening with custom expiry (default: 7 days)  
✅ Automatic TTL-based cleanup (no manual deletion)  
✅ Load-balanced across multiple instances  
✅ Distributed database with Cassandra  
✅ Container-based deployment  
✅ URL validation  
✅ Health checks & monitoring

## Configuration

**Environment Variables:**
- `CASSANDRA_HOST` - Database hostname (default: `cassandra` in Docker)
- `BASE_URL` - Short URL prefix (in `main.py`)

**Scaling:**
Add more app instances in `docker-compose.yml`:
```yaml
app3:
  build: .
  ports: ["8003:8000"]
  environment:
    - CASSANDRA_HOST=cassandra
```
Then update `nginx/nginx.conf` to include the new instance.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `docker-compose.yml` |
| Cassandra unhealthy | Wait 40+ seconds for startup, check `docker-compose logs cassandra` |
| Module import error | Ensure Dockerfile has `COPY . .` and `WORKDIR /app` |
| Connection refused | Verify `CASSANDRA_HOST` environment variable is set correctly |

## Example Usage

```bash
# Create short URL
curl -X POST "http://localhost:8090/shorten?long_url=https://github.com&expiry_days=30"

# Use short URL (redirects)
curl -L "http://localhost:8090/abc123"

# Check service health
curl http://localhost:8090/healthcheck
```

## Development

Local setup:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

View logs:
```bash
docker-compose logs -f
```

Stop services:
```bash
docker-compose down
```