# Server Patterns

Patterns for configuring Apollo server components.

## gRPC Server

### Basic Configuration
```hocon
grpc.server {
  port: 5990
  metrics.enabled: true
  deadlineEnforcer.enabled: true
  reflection.enabled: true
}
```

### Full Configuration
```hocon
grpc.server {
  # Port configuration
  port: 5990
  port: ${?GRPC_PORT}

  # Metrics
  metrics.enabled: true

  # Deadline enforcement
  deadlineEnforcer {
    enabled: true
    defaultDeadline: 30s
  }

  # Reflection (for grpcurl)
  reflection.enabled: true

  # Thread pool
  executor {
    type: fixed
    threads: 16
  }

  # Max message size (default 4MB)
  maxInboundMessageSize: 16777216  # 16MB
}
```

### Key Settings
| Setting | Default | Description |
|---------|---------|-------------|
| port | 5990 | gRPC listen port |
| metrics.enabled | true | Enable Prometheus metrics |
| deadlineEnforcer.enabled | true | Enforce client deadlines |
| reflection.enabled | true | Enable gRPC reflection |

## HTTP Server

### Basic Configuration
```hocon
http.server {
  port: 8080
}
```

### With CORS
```hocon
http.server {
  port: 8080
  cors {
    enabled: true
    origins: ["https://backstage.spotify.net", "https://my-app.spotify.net"]
    methods: ["GET", "POST", "PUT", "DELETE"]
    allowCredentials: true
  }
}
```

### With TLS
```hocon
http.server {
  port: 8443
  ssl {
    enabled: true
    keyStore: "/etc/spotify/secrets/keystore.p12"
    keyStorePassword: ${?SSL_KEYSTORE_PASSWORD}
  }
}
```

## Hermes Server

### Basic Configuration
```hocon
hermes.server {
  enabled: true
  port: 5700
}
```

## Apollo Core Settings

### Logging
```hocon
apollo {
  logIncomingRequests: false   # Disable for production (too verbose)
  logOutgoingRequests: false
  logLevel: INFO
  logLevel: ${?LOG_LEVEL}
}
```

### Shutdown
```hocon
apollo {
  gracefulShutdownTimeout: 30s
}
```

## Environment-Specific Configuration

### Development
```hocon
grpc.server {
  reflection.enabled: true  # Enable for debugging
}

apollo {
  logIncomingRequests: true  # Enable for debugging
}
```

### Production
```hocon
grpc.server {
  reflection.enabled: false  # Disable for security
}

apollo {
  logIncomingRequests: false
}
```
