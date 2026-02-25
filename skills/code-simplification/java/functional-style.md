# Functional Style Patterns

## Streams vs Traditional Loops

### Pattern: Filter-Map-Collect

Before:

```java
List<String> activeUserEmails = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) {
        activeUserEmails.add(user.getEmail());
    }
}
```

After:

```java
List<String> activeUserEmails = users.stream()
    .filter(User::isActive)
    .map(User::getEmail)
    .toList();
```

### Pattern: Find First Match

Before:

```java
User admin = null;
for (User user : users) {
    if (user.getRole() == Role.ADMIN) {
        admin = user;
        break;
    }
}
if (admin == null) {
    throw new NotFoundException("No admin found");
}
```

After:

```java
User admin = users.stream()
    .filter(user -> user.getRole() == Role.ADMIN)
    .findFirst()
    .orElseThrow(() -> new NotFoundException("No admin found"));
```

### Pattern: Grouping

Before:

```java
Map<Department, List<Employee>> byDepartment = new HashMap<>();
for (Employee emp : employees) {
    Department dept = emp.getDepartment();
    if (!byDepartment.containsKey(dept)) {
        byDepartment.put(dept, new ArrayList<>());
    }
    byDepartment.get(dept).add(emp);
}
```

After:

```java
Map<Department, List<Employee>> byDepartment = employees.stream()
    .collect(groupingBy(Employee::getDepartment));
```

### Pattern: Reduce / Aggregate

Before:

```java
int totalQuantity = 0;
for (OrderItem item : order.getItems()) {
    totalQuantity += item.getQuantity();
}
```

After:

```java
int totalQuantity = order.getItems().stream()
    .mapToInt(OrderItem::getQuantity)
    .sum();
```

### Pattern: Any Match / All Match

Before:

```java
boolean hasExpiredItem = false;
for (Item item : items) {
    if (item.isExpired()) {
        hasExpiredItem = true;
        break;
    }
}
```

After:

```java
boolean hasExpiredItem = items.stream().anyMatch(Item::isExpired);
```

## Optional Patterns

### Pattern: Null-Safe Chain

Before:

```java
String city = null;
if (user != null) {
    Address address = user.getAddress();
    if (address != null) {
        city = address.getCity();
    }
}
return city != null ? city : "Unknown";
```

After:

```java
return Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");
```

### Pattern: Conditional Execution

Before:

```java
if (user != null) {
    sendWelcomeEmail(user);
}
```

After:

```java
Optional.ofNullable(user).ifPresent(this::sendWelcomeEmail);
```

### Pattern: Transform or Default

Before:

```java
String displayName;
if (user.getNickname() != null) {
    displayName = user.getNickname().toUpperCase();
} else {
    displayName = user.getEmail();
}
```

After:

```java
String displayName = Optional.ofNullable(user.getNickname())
    .map(String::toUpperCase)
    .orElseGet(user::getEmail);
```

### Pattern: Throw if Empty

Before:

```java
User user = userRepository.findById(id);
if (user == null) {
    throw new UserNotFoundException("User not found: " + id);
}
return user;
```

After:

```java
return userRepository.findById(id)
    .orElseThrow(() -> new UserNotFoundException("User not found: " + id));
```

**Note**: This assumes `findById` returns `Optional<User>`. If it returns nullable, wrap with `Optional.ofNullable()`.

## Lambda Simplification

### Pattern: Method Reference

Before:

```java
users.forEach(user -> System.out.println(user));
users.stream().map(user -> user.getName());
users.stream().filter(user -> user.isActive());
```

After:

```java
users.forEach(System.out::println);
users.stream().map(User::getName);
users.stream().filter(User::isActive);
```

### Pattern: Constructor Reference

Before:

```java
List<User> users = names.stream()
    .map(name -> new User(name))
    .toList();
```

After:

```java
List<User> users = names.stream()
    .map(User::new)
    .toList();
```

### Pattern: Single-Expression Lambda

Before:

```java
Comparator<User> byName = (u1, u2) -> {
    return u1.getName().compareTo(u2.getName());
};
```

After:

```java
Comparator<User> byName = Comparator.comparing(User::getName);
```
