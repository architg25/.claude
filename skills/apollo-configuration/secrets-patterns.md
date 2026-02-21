# Secrets Patterns

Patterns for managing secrets in Apollo configuration.

## File Include Pattern

### Basic Secret Injection
```hocon
# In main config
jdbc {
  url: "jdbc:postgresql://localhost:5433/mydb"
}

# Inject secrets (overrides/adds to jdbc object)
jdbc: { include file("/etc/spotify/secrets/database.json") }
```

### Secret File Format
```json
// /etc/spotify/secrets/database.json
{
  "username": "myuser",
  "password": "mysecretpassword"
}
```

## Environment Variable Pattern

### Optional Override
```hocon
# Default value with optional env override
jdbc.url = "jdbc:postgresql://localhost:5433/mydb"
jdbc.url = ${?POSTGRES_JDBC_URL}
```

### Required Environment Variable
```hocon
# Will fail if not set
api.key = ${API_KEY}
```

### Optional with Fallback
```hocon
# Use env var if set, otherwise use default
log.level = "INFO"
log.level = ${?LOG_LEVEL}
```

## Spotify Secret Paths

### Standard Paths
| Secret Type | Path |
|-------------|------|
| Service credentials | `/etc/spotify/secrets/service.json` |
| Database credentials | `/etc/spotify/secrets/database.json` |
| API keys | `/etc/spotify/secrets/api-keys.json` |
| Service account | `/var/secrets/google/service-account.json` |

### Multiple Secrets
```hocon
# Include multiple secret files
database: { include file("/etc/spotify/secrets/database.json") }
external-api: { include file("/etc/spotify/secrets/external-api.json") }
```

## Google Secret Manager (with Gantry)

When using Gantry, secrets are injected via `secretRefs`:

```yaml
# In gantry.yaml
secretRefs:
  - gcpProjectId: my-project
    secrets:
      - gsmKey: database-password
        envVar: DB_PASSWORD
```

Then reference in config:
```hocon
jdbc.password = ${?DB_PASSWORD}
```

## Best Practices

### DO
```hocon
# Use optional substitution
password = ${?SECRET_PASSWORD}

# Use file include for complex secrets
credentials: { include file("/etc/spotify/secrets/creds.json") }

# Use descriptive names
database.password = ${?DB_PASSWORD}
```

### DON'T
```hocon
# Never hardcode secrets
password = "my-secret-password"  # WRONG!

# Never commit secrets
api.key = "abc123"  # WRONG!

# Never use required substitution for secrets in local dev
password = ${SECRET_PASSWORD}  # Will fail if not set
```

## Local Development

### Using .env Files
```bash
# .env (git-ignored)
POSTGRES_JDBC_URL=jdbc:postgresql://localhost:5433/mydb
DB_PASSWORD=localdevpassword
```

### Using application-local.conf
```hocon
# src/main/resources/application-local.conf (git-ignored)
include "application.conf"

jdbc {
  url: "jdbc:postgresql://localhost:5433/mydb"
  username: "localuser"
  password: "localpassword"
}
```
