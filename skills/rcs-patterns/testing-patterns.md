# Testing Patterns

Testing RCS property resolution before launch.

## Backstage Remote Config Plugin

Test resolution for specific users via Backstage UI:
https://backstage.spotify.net/experimentation

### Steps
1. Navigate to your property in Backstage
2. Enter test user ID
3. View resolved value and applied policies
4. Verify targeting works as expected

## Override Testing

Force specific values for QA:

### Backstage Overrides
1. Go to Experimentation Platform UI
2. Select experiment/rollout
3. Add user override with specific variant

### Code-Level Testing
```java
// In tests, mock the configuration
Configuration mockConfig = mock(Configuration.class);
when(mockConfig.get(ENABLE_FEATURE)).thenReturn(true);
```

## Pre-Launch Checklist

| Check | How |
|-------|-----|
| Default works | Resolve with no policies |
| Targeting correct | Test with target user |
| Non-target excluded | Test with excluded user |
| Fallback behavior | Disable RCS, verify defaults |
