---
name: kubernetes-deployments
description: Standard Kubernetes deployment patterns for Apollo/backend services at Spotify. Covers Deployment, Service, HPA, PDB, ConfigMap, Runtime CRD, resource sizing, Kustomize patterns, and Gantry migration. Use when creating or configuring Kubernetes manifests for backend services.
allowed-tools:
  - Read
---

# Kubernetes Deployment Patterns

Patterns for deploying Apollo/backend services to Kubernetes at Spotify.

## Pattern Categories

- **[Runtime Patterns](runtime-patterns.md)**: Spotify Runtime CRD for namespace setup (START HERE for new services)
- **[Deployment Patterns](deployment-patterns.md)**: Resource requests, probes, rolling updates
- **[Service Patterns](service-patterns.md)**: ClusterIP, annotations, port conventions
- **[HPA Patterns](hpa-patterns.md)**: Horizontal Pod Autoscaler configuration
- **[PDB Patterns](pdb-patterns.md)**: Pod Disruption Budgets for availability
- **[Kustomize Patterns](kustomize-patterns.md)**: Directory structure, overlays, environments
- **[Gantry Patterns](gantry-patterns.md)**: New deployment standard replacing Kustomize/Tugboat
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Quick Reference

### Standard Ports
| Port | Purpose |
|------|---------|
| 5700 | Health monitoring (hm) |
| 5701 | Health monitoring snoop (hm-snoop) |
| 5990 | gRPC |
| 8080 | HTTP |

### Resource Sizing Defaults
| Setting | Starting Value | Notes |
|---------|---------------|-------|
| CPU Request | 4 cores | Adjust based on metrics |
| CPU Limit | 6 cores | |
| Memory Request/Limit | 8GB | Set equal to prevent OOM |
| Max pod size | ≤15 cores | For scheduling |
| Memory ratio | 1:4 vCPU:GiB | Recommendation |

### HPA Defaults
| Setting | Value | Reason |
|---------|-------|--------|
| Target CPU | 80% | Spotify standard |
| Min replicas | 3 | Availability |
| Scale-down cooldown | 30 min | Prevent flapping |

### Image Placeholder
```yaml
image: $DEPLOYMENT_IMAGE  # CI/CD injects actual image
```

### Kustomize vs Gantry Decision

| Situation | Use |
|-----------|-----|
| New service | **Gantry** (single gantry.yaml) |
| Existing Kustomize service | Migrate to Gantry by Spring 2026 |
| Complex custom requirements | Check Gantry feature support first |

## Critical Constraints

- **Always** set memory request = limit (prevents OOM)
- **Always** use 3+ replicas for production
- **Always** include readiness and liveness probes
- **Always** use `$DEPLOYMENT_IMAGE` placeholder (Tingle/Tugboat substitutes)
- **Always** create Runtime CRD before Deployment
- **Never** use memory-based HPA for Java services (kills warm caches)
- **Never** set CPU limits too tight (causes throttling)
- **Never** create new Kustomize configurations (use Gantry instead)

## Tooling

| Tool | Purpose | Usage |
|------|---------|-------|
| Tugboat | Deployment validation | `tugboat version <component> validate` |
| gantryctl | Gantry management | `bazel run //gantry/gantryctl -- get service <project> <service>` |
| kubectl-site | Cluster context switching | `kubectl site <service-name>` |
| kubernetes-templates | Standard manifests | Clone from repo |

## Related Skills

- [locus-caching](../locus-caching/SKILL.md) - Locus CRD for caching
- [mma-templates](../mma-templates/SKILL.md) - Monitoring configuration
- [apollo-configuration](../apollo-configuration/SKILL.md) - HOCON/.conf patterns

## Documentation Links

- [GKE Rightsizing](https://backstage.spotify.net/docs/default/component/gke/developers/rightsizing/scaling/)
- [Services Pilot](https://backstage.spotify.net/docs/default/component/services-pilot/)
- [kubernetes-templates repo](https://ghe.spotify.net/kubernetes/kubernetes-templates)
- [Gantry Docs](https://backstage.spotify.net/docs/default/component/gantry-docs/)
- [Runtime Operator](https://backstage.spotify.net/docs/default/component/runtime-operator/)

## Support Channels

- #deployments-support - Primary deployment issues
- #declarative-infra - Runtime resources
- #warpspeed - Testing environment
