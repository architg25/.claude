# Database Patterns

Patterns for configuring database connections in Apollo services.

## JDBC Connection

### Basic Configuration
```hocon
jdbc {
  url: "jdbc:postgresql://localhost:5433/mydb"
  url: ${?POSTGRES_JDBC_URL}

  pool: {
    max-total: 20
    min-idle: 2
  }
}
```

### With Credentials
```hocon
jdbc {
  url: "jdbc:postgresql://localhost:5433/mydb"
  url: ${?POSTGRES_JDBC_URL}

  username: "myuser"
  username: ${?POSTGRES_USER}

  password: ${?POSTGRES_PASSWORD}

  pool: {
    max-total: 20
    min-idle: 2
    max-idle: 10
  }
}

# Inject secrets
jdbc: { include file("/etc/spotify/secrets/database.json") }
```

## Connection Pool Sizing

### Sizing Guidelines
| Service Type | max-total | min-idle |
|-------------|-----------|----------|
| Low traffic | 10 | 2 |
| Medium traffic | 20 | 5 |
| High traffic | 50 | 10 |
| Batch processing | 100 | 20 |

### Full Pool Configuration
```hocon
jdbc {
  pool: {
    # Pool sizes
    max-total: 20
    min-idle: 2
    max-idle: 10

    # Timeouts
    max-wait-millis: 10000  # Wait for connection

    # Eviction
    time-between-eviction-runs-millis: 60000
    min-evictable-idle-time-millis: 300000

    # Validation
    test-on-borrow: true
    validation-query: "SELECT 1"
  }
}
```

## Cloud SQL

### PostgreSQL
```hocon
jdbc {
  url: "jdbc:postgresql:///mydb?cloudSqlInstance=project:region:instance&socketFactory=com.google.cloud.sql.postgres.SocketFactory"
  url: ${?POSTGRES_JDBC_URL}
}
```

### MySQL
```hocon
jdbc {
  url: "jdbc:mysql:///mydb?cloudSqlInstance=project:region:instance&socketFactory=com.google.cloud.sql.mysql.SocketFactory"
  url: ${?MYSQL_JDBC_URL}
}
```

## Multiple Databases

```hocon
# Primary database
jdbc.primary {
  url: ${?PRIMARY_JDBC_URL}
  pool.max-total: 20
}

# Read replica
jdbc.replica {
  url: ${?REPLICA_JDBC_URL}
  pool.max-total: 10
}

# Inject credentials
jdbc.primary: { include file("/etc/spotify/secrets/primary-db.json") }
jdbc.replica: { include file("/etc/spotify/secrets/replica-db.json") }
```

## Caching Configuration (Caffeine/JCache)

```hocon
caffeine.jcache {
  caches {
    "my-cache" {
      spec: "maximumSize=10000,expireAfterWrite=5m"
    }
  }
}
```
