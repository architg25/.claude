---
name: apollo-configuration
description: HOCON/.conf patterns for Apollo framework services at Spotify. Covers gRPC server/client, HTTP server, Hermes, database connections, and secret injection. Use when configuring Apollo backend services.
allowed-tools:
  - Read
---

# Apollo Configuration Patterns

Patterns for configuring Apollo framework services using HOCON.

## Pattern Categories

- **[Server Patterns](server-patterns.md)**: grpc.server, http.server, hermes.server
- **[Client Patterns](client-patterns.md)**: grpc.client, hermes.client configuration
- **[Database Patterns](database-patterns.md)**: JDBC connection pools
- **[Secrets Patterns](secrets-patterns.md)**: File includes, environment variables
- **[Troubleshooting](troubleshooting.md)**: Common configuration issues

## Quick Reference

### File Location
```
src/main/resources/{{service-name}}.conf
```

### Basic Apollo Config
```hocon
apollo {
  logIncomingRequests: false
  logOutgoingRequests: false
}

grpc.server {
  port: 5990
  metrics.enabled: true
  deadlineEnforcer.enabled: true
  reflection.enabled: true
}

http.server {
  port: 8080
}
```

### Environment Variable Override
```hocon
# Default with environment override
jdbc.url = "jdbc:postgresql://localhost:5433/mydb"
jdbc.url = ${?POSTGRES_JDBC_URL}
```

### Secret Injection
```hocon
jdbc: { include file("/etc/spotify/secrets/service.json") }
```

## HOCON Features

| Feature | Syntax | Example |
|---------|--------|---------|
| Env override | `${?VAR}` | `port = ${?HTTP_PORT}` |
| File include | `include file()` | `include file("/path")` |
| Object merge | `{}` | `a { b: 1 }` |
| Substitution | `${}` | `url = ${base}/path` |
| Optional | `${?VAR}` | Won't fail if VAR unset |

## Critical Constraints

- **Always** use `${?VAR}` (optional) for environment overrides
- **Always** put secrets in `/etc/spotify/secrets/`
- **Never** hardcode credentials in .conf files
- **Never** commit secrets to version control

## Related Skills

- [kubernetes-deployments](../kubernetes-deployments/SKILL.md) - K8s deployment patterns
- [decibel](../decibel/SKILL.md) - Database schema patterns

## Documentation Links

- [Apollo Framework](https://backstage.spotify.net/docs/default/component/apollo/)
- [Hermes Client](https://backstage.spotify.net/docs/default/component/hermes/)

## Support Channels

- #apollo-users - Apollo framework support
- #grpc-users - gRPC-specific questions
