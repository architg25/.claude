# Property Types

Complete reference for RCS property type definitions.

## Boolean Properties

Most common type for feature flags.

### Java Definition
```java
public static final BooleanPropertyDefinition ENABLE_FEATURE =
    PropertyDefinitions.booleanProperty("enable_feature")
        .withDefault(false)
        .withDescription("Enables the new feature");
```

### Mobile Definition (properties.yaml)
```yaml
properties:
  - name: enable_feature
    type: boolean
    default: false
    description: "Enables the new feature"
```

## Integer Properties

For thresholds, limits, and numeric configuration.

### Java Definition
```java
public static final IntegerPropertyDefinition MAX_RETRIES =
    PropertyDefinitions.integerProperty("max_retries")
        .withDefault(3)
        .withDescription("Maximum retry attempts");
```

### Mobile Definition
```yaml
properties:
  - name: max_retries
    type: integer
    default: 3
    description: "Maximum retry attempts"
```

## Enum Properties

For selecting between predefined options.

### Java Definition
```java
public static final EnumPropertyDefinition<Algorithm> SEARCH_ALGORITHM =
    PropertyDefinitions.enumProperty("search_algorithm", Algorithm.class)
        .withDefault(Algorithm.V1)
        .withDescription("Search algorithm version");
```

### Mobile Definition
```yaml
properties:
  - name: search_algorithm
    type: enum
    values: [v1, v2, v3]
    default: v1
    description: "Search algorithm version"
```

## StringSet Properties

For allow/deny lists and market targeting.

### Java Definition
```java
public static final StringSetPropertyDefinition ENABLED_MARKETS =
    PropertyDefinitions.stringSetProperty("enabled_markets")
        .withDefault(Set.of("US", "GB"))
        .withDescription("Markets where feature is enabled");
```

## Best Practices

| Practice | Reason |
|----------|--------|
| Use descriptive names | Clarity in EP UI |
| Set safe defaults | Graceful degradation |
| Document purpose | Team understanding |
| Namespace by feature | Avoid collisions |
