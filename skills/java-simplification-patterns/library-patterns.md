# Library Patterns

## Guava Collections

### Pattern: Immutable Collections

Before:
```java
List<String> list = new ArrayList<>();
list.add("a");
list.add("b");
list = Collections.unmodifiableList(list);
```

After:
```java
List<String> list = ImmutableList.of("a", "b");
```

### Pattern: Multimap

Before:
```java
Map<Department, List<Employee>> byDept = new HashMap<>();
for (Employee emp : employees) {
    Department dept = emp.getDepartment();
    if (!byDept.containsKey(dept)) {
        byDept.put(dept, new ArrayList<>());
    }
    byDept.get(dept).add(emp);
}
```

After:
```java
ImmutableListMultimap<Department, Employee> byDept = employees.stream()
    .collect(toImmutableListMultimap(Employee::getDepartment, Function.identity()));
```

**Note**: For mutable Multimap (if mutability is required):
```java
Multimap<Department, Employee> byDept = employees.stream()
    .collect(Multimaps.toMultimap(
        Employee::getDepartment,
        Function.identity(),
        ArrayListMultimap::create));
```

## Guava Utilities

### Pattern: String Utilities

Before:
```java
if (str == null || str.isEmpty()) {
    return defaultValue;
}
```

After:
```java
import static com.google.common.base.Strings.*;

if (isNullOrEmpty(str)) {
    return defaultValue;
}
```

### Pattern: Preconditions

Before:
```java
public void process(Order order) {
    if (order == null) {
        throw new IllegalArgumentException("order cannot be null");
    }
    if (order.getItems().isEmpty()) {
        throw new IllegalArgumentException("order must have items");
    }
    if (order.getTotal().compareTo(BigDecimal.ZERO) <= 0) {
        throw new IllegalArgumentException("order total must be positive");
    }
    // ... process
}
```

After:
```java
import static com.google.common.base.Preconditions.*;

public void process(Order order) {
    checkNotNull(order, "order cannot be null");
    checkArgument(!order.getItems().isEmpty(), "order must have items");
    checkArgument(order.getTotal().compareTo(BigDecimal.ZERO) > 0,
        "order total must be positive");
    // ... process
}
```

## Lombok

### Pattern: Data Classes

Before:
```java
public class User {
    private Long id;
    private String name;
    private String email;

    public User() {}

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    @Override
    public boolean equals(Object o) { /* ... */ }

    @Override
    public int hashCode() { /* ... */ }

    @Override
    public String toString() { /* ... */ }
}
```

After:
```java
@Data
public class User {
    private Long id;
    private String name;
    private String email;
}
```

### Pattern: Builder

Before:
```java
public class Request {
    private final String url;
    private final String method;
    private final Map<String, String> headers;
    private final String body;

    private Request(Builder builder) {
        this.url = builder.url;
        this.method = builder.method;
        this.headers = builder.headers;
        this.body = builder.body;
    }

    public static class Builder {
        private String url;
        private String method = "GET";
        private Map<String, String> headers = new HashMap<>();
        private String body;

        public Builder url(String url) {
            this.url = url;
            return this;
        }
        // ... more builder methods

        public Request build() {
            return new Request(this);
        }
    }
}
```

After:
```java
@Builder
@Value
public class Request {
    String url;
    @Builder.Default String method = "GET";
    @Singular Map<String, String> headers;
    String body;
}
```

### Pattern: Immutable Value Objects

Before:
```java
public final class Money {
    private final BigDecimal amount;
    private final Currency currency;

    public Money(BigDecimal amount, Currency currency) {
        this.amount = amount;
        this.currency = currency;
    }

    public BigDecimal getAmount() { return amount; }
    public Currency getCurrency() { return currency; }

    @Override
    public boolean equals(Object o) { /* ... */ }

    @Override
    public int hashCode() { /* ... */ }

    @Override
    public String toString() { /* ... */ }
}
```

After:
```java
@Value
public class Money {
    BigDecimal amount;
    Currency currency;
}
```

**Note**: Consider Java records for simple immutable data holders (Java 16+):
```java
public record Money(BigDecimal amount, Currency currency) {}
```
