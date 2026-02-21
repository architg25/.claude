# Mobile SDK Patterns

iOS, Android, and Web patterns for RCS properties.

## properties.yaml Structure

```yaml
# Located in your mobile project
properties:
  - name: enable_feature
    type: boolean
    default: false
    description: "Enables the new feature"

  - name: max_items
    type: integer
    default: 10
    description: "Maximum items to display"
```

## Publishing Properties

Use `rc_tool.pyz` CLI:

```bash
# Publish to RCS
python rc_tool.pyz publish --config properties.yaml
```

## Property Access (iOS)

```swift
let enabled = RemoteConfig.shared.get("enable_feature", default: false)
```

## Property Access (Android)

```kotlin
val enabled = remoteConfig.getBoolean("enable_feature", false)
```

## Propagation Delay

Mobile properties use offline resolution with bloom filters:

| Platform | Typical Delay |
|----------|---------------|
| iOS | 1-3 days |
| Android | 1-3 days |
| Web | Minutes (online) |

**Important**: Account for this delay when:
- Starting experiments (wait for propagation)
- Analyzing metrics (users may not have new config)
- Comparing mobile vs backend exposure timing
