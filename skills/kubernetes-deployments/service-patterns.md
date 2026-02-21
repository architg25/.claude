# Service Patterns

Patterns for configuring Kubernetes Services for Apollo services.

## Basic ClusterIP Service

**Use when**: Internal service communication

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
  namespace: my-namespace
  annotations:
    nameless.spotify.com/srv-expose: "true"
spec:
  type: ClusterIP
  selector:
    app: my-service
  ports:
    - name: grpc
      port: 5990
      targetPort: 5990
    - name: http
      port: 8080
      targetPort: 8080
    - name: hm
      port: 5700
      targetPort: 5700
    - name: hm-snoop
      port: 5701
      targetPort: 5701
```

## Standard Port Mappings

| Port | Name | Purpose |
|------|------|---------|
| 5700 | hm | Health monitoring |
| 5701 | hm-snoop | Health monitoring snoop |
| 5990 | grpc | gRPC traffic |
| 8080 | http | HTTP traffic |

## Annotations

### Nameless Service Discovery
```yaml
annotations:
  nameless.spotify.com/srv-expose: "true"
```
Registers service with Nameless for `nls://` resolution.

### Prometheus Scraping
```yaml
annotations:
  prometheus.spotify.net/scrape: "true"
  prometheus.spotify.net/port: "5700"
```

## gRPC-Only Service

**Use when**: Service only exposes gRPC

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-grpc-service
  namespace: my-namespace
  annotations:
    nameless.spotify.com/srv-expose: "true"
spec:
  type: ClusterIP
  selector:
    app: my-grpc-service
  ports:
    - name: grpc
      port: 5990
      targetPort: 5990
    - name: hm
      port: 5700
      targetPort: 5700
```

## HTTP-Only Service

**Use when**: Service only exposes HTTP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-http-service
  namespace: my-namespace
  annotations:
    nameless.spotify.com/srv-expose: "true"
spec:
  type: ClusterIP
  selector:
    app: my-http-service
  ports:
    - name: http
      port: 8080
      targetPort: 8080
    - name: hm
      port: 5700
      targetPort: 5700
```

## Headless Service

**Use when**: Direct pod DNS resolution needed

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service-headless
  namespace: my-namespace
spec:
  type: ClusterIP
  clusterIP: None
  selector:
    app: my-service
  ports:
    - name: grpc
      port: 5990
```

## Session Affinity

**Use when**: Sticky sessions required

```yaml
spec:
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800  # 3 hours
```
