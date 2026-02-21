# Resolution Patterns

Online vs Offline resolution modes and when to use each.

## Online Resolution (Pizza)

Real-time configuration fetching from RCS service.

### When to Use
- Need immediate configuration updates
- Require user registration date targeting
- Need external user attributes
- Complex platform/version targeting
- Full client attribute support needed

### Characteristics
| Aspect | Value |
|--------|-------|
| Latency | Higher (network call) |
| Freshness | Real-time |
| Targeting | Full support |
| Availability | Requires RCS service |

## Offline Resolution (Bloom Filters)

Cached policies evaluated locally.

### When to Use
- Low latency critical
- Simple targeting sufficient
- Mobile/client applications

### Supported Targeting (Offline Only)
| Attribute | Support |
|-----------|---------|
| `user_id` | Full |
| `country` | Full |
| `catalogue` | Full |
| `employee` | Full |
| Platform (Android/iOS main) | Limited |

### NOT Supported Offline
- Registration date targeting
- External user attributes
- Full platform/client targeting
- Client version (best-effort only)
- Complex BigQuery targeting

## Decision Flow

```
Need real-time updates?
├── Yes → Online (Pizza)
└── No
    ├── Need user attributes? → Online (Pizza)
    └── Simple user/country targeting?
        └── Yes → Offline (bloom filters)
```

## Sources
- https://backstage.spotify.net/docs/default/component/user-policy/#silent-failures-of-property-evaluation
- https://backstage.spotify.net/docs/default/component/remote-config-client-java/remote-config-offline-client/
