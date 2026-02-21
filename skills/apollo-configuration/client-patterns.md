# Client Patterns

Patterns for configuring Apollo client components.

## gRPC Client

### Basic Configuration
```hocon
grpc.client {
  useForkJoinPool: true
  executorThreads: 8
}
```

### With ELS/ORCA (Load Balancing)
```hocon
grpc.client {
  useForkJoinPool: true
  executorThreads: 8

  els {
    enabled: true
    orca.enabled: true
  }
}
```

### Connection Settings
```hocon
grpc.client {
  # Thread pool
  useForkJoinPool: true
  executorThreads: 8

  # Timeouts
  defaultDeadline: 10s

  # Connection pool
  maxConcurrentStreams: 100

  # Keep-alive
  keepAlive {
    time: 30s
    timeout: 10s
    permitWithoutCalls: false
  }
}
```

## Hermes Client

### Basic Configuration
```hocon
hermes.client {
  outstandingRequestLimit: 800
}
```

### Full Configuration
```hocon
hermes.client {
  # Request limits
  outstandingRequestLimit: 800

  # Timeouts
  requestTimeout: 10s
  connectTimeout: 5s

  # Retry configuration
  retries {
    maxAttempts: 3
    backoff {
      initial: 100ms
      max: 1s
      multiplier: 2.0
    }
  }
}
```

### Key Settings
| Setting | Default | Description |
|---------|---------|-------------|
| outstandingRequestLimit | 800 | Max concurrent requests |
| requestTimeout | 10s | Per-request timeout |
| maxAttempts | 3 | Retry attempts |

## Service-Specific Clients

### Named Client Configuration
```hocon
grpc.client {
  # Default settings
  useForkJoinPool: true
  executorThreads: 8

  # Override for specific service
  targets {
    "my-downstream-service" {
      defaultDeadline: 5s
      maxConcurrentStreams: 50
    }
  }
}
```

## Circuit Breaker

### Basic Circuit Breaker
```hocon
grpc.client {
  circuitBreaker {
    enabled: true
    failureThreshold: 5
    successThreshold: 3
    timeout: 30s
  }
}
```
