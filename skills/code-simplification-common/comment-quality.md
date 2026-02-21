# Comment Quality

## WHY, Not WHAT

Comments should explain reasoning, not describe what the code does.

### Pattern: Explain Intent

Before:
```
// Loop through users
for (User user : users) {
    // Check if user is active
    if (user.isActive()) {
        // Add to result list
        result.add(user);
    }
}
```

After:
```
// Filter to active users only - inactive users are pending deletion
// and should not appear in search results (see JIRA-1234)
List<User> activeUsers = users.stream()
    .filter(User::isActive)
    .toList();
```

## Self-Documenting Code

Clear naming reduces the need for comments.

### Pattern: Replace Comments with Clear Names

Before:
```
// Calculate the total price including tax and shipping
double calc(Order o) {
    double st = 0;  // subtotal
    for (Item i : o.items) {
        st += i.p * i.q;  // price * quantity
    }
    double t = st * 0.08;  // tax at 8%
    double s = st > 100 ? 0 : 5.99;  // free shipping over $100
    return st + t + s;
}
```

After:
```
Money calculateTotalPrice(Order order) {
    Money subtotal = calculateSubtotal(order);
    Money tax = calculateTax(subtotal);
    Money shipping = calculateShipping(subtotal);
    return subtotal.add(tax).add(shipping);
}

private Money calculateTax(Money subtotal) {
    return subtotal.multiply(TAX_RATE);
}

private Money calculateShipping(Money subtotal) {
    return subtotal.isGreaterThan(FREE_SHIPPING_THRESHOLD)
        ? Money.ZERO
        : STANDARD_SHIPPING_COST;
}
```

## Outdated Comments

Outdated comments are worse than no comments.

Before:
```
// Returns the user's full name (first + last)
String getUserDisplayName(User user) {
    // Actually now returns nickname if set, otherwise email
    return user.getNickname() != null
        ? user.getNickname()
        : user.getEmail();
}
```

After:
```
String getUserDisplayName(User user) {
    return user.getNickname() != null
        ? user.getNickname()
        : user.getEmail();
}
```

Or if context is needed:
```
/**
 * Returns the user's preferred display name.
 * Falls back to email if no nickname is set.
 */
String getUserDisplayName(User user) {
    return Optional.ofNullable(user.getNickname())
        .orElse(user.getEmail());
}
```

## TODO Hygiene

TODOs should have owners or ticket references.

Before:
```
// TODO: fix this later
// TODO: refactor
// TODO: handle edge case
```

After:
```
// TODO(jsmith): Handle pagination - JIRA-5678
// TODO(@team-platform): Migrate to new API before Q3 deprecation
```

Or better: Create a ticket and remove the TODO.

## API Documentation

Public APIs need clear contracts.

### Pattern: Document Contracts, Not Implementation

Before:
```
/**
 * This method finds a user. It queries the database
 * using a SELECT statement with the id parameter.
 * Then it maps the ResultSet to a User object.
 */
User findById(Long id);
```

After:
```
/**
 * Finds a user by their unique identifier.
 *
 * @param id the user's unique identifier, must not be null
 * @return the user if found
 * @throws UserNotFoundException if no user exists with the given id
 * @throws IllegalArgumentException if id is null
 */
User findById(Long id);
```
