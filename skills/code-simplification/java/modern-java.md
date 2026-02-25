# Modern Java Features (21/25)

## Java 21 Features (LTS)

### Pattern Matching for Switch (JEP 441)

Eliminates verbose if-else instanceof chains.

Before:

```java
static String formatter(Object obj) {
    String formatted = "unknown";
    if (obj instanceof Integer i) {
        formatted = String.format("int %d", i);
    } else if (obj instanceof Long l) {
        formatted = String.format("long %d", l);
    } else if (obj instanceof Double d) {
        formatted = String.format("double %f", d);
    } else if (obj instanceof String s) {
        formatted = String.format("String %s", s);
    }
    return formatted;
}
```

After:

```java
static String formatter(Object obj) {
    return switch (obj) {
        case Integer i -> String.format("int %d", i);
        case Long l -> String.format("long %d", l);
        case Double d -> String.format("double %f", d);
        case String s -> String.format("String %s", s);
        default -> "unknown";
    };
}
```

**Why**: Provides exhaustiveness checking, more concise, clearer intent.

### Null Handling in Switch (JEP 441)

Removes external null checks.

Before:

```java
static void process(String s) {
    if (s == null) {
        System.out.println("Null value!");
        return;
    }
    switch (s) {
        case "A" -> System.out.println("Got A");
        case "B" -> System.out.println("Got B");
        default -> System.out.println("Other");
    }
}
```

After:

```java
static void process(String s) {
    switch (s) {
        case null -> System.out.println("Null value!");
        case "A" -> System.out.println("Got A");
        case "B" -> System.out.println("Got B");
        default -> System.out.println("Other");
    }
}
```

**Why**: Handles null uniformly with other cases, reduces boilerplate.

### Record Patterns (JEP 440)

Enables direct record destructuring.

Before:

```java
record Point(int x, int y) {}

void printSum(Object obj) {
    if (obj instanceof Point p) {
        int x = p.x();
        int y = p.y();
        System.out.println(x + y);
    }
}
```

After:

```java
void printSum(Object obj) {
    if (obj instanceof Point(int x, int y)) {
        System.out.println(x + y);
    }
}
```

**Why**: Eliminates explicit accessor calls, direct destructuring.

### Nested Record Patterns

Before:

```java
record Point(int x, int y) {}
record Rectangle(Point upperLeft, Point lowerRight) {}

void processRectangle(Object obj) {
    if (obj instanceof Rectangle r) {
        Point ul = r.upperLeft();
        Point lr = r.lowerRight();
        int width = lr.x() - ul.x();
        int height = lr.y() - ul.y();
        System.out.println("Area: " + (width * height));
    }
}
```

After:

```java
void processRectangle(Object obj) {
    if (obj instanceof Rectangle(Point(int x1, int y1), Point(int x2, int y2))) {
        int width = x2 - x1;
        int height = y2 - y1;
        System.out.println("Area: " + (width * height));
    }
}
```

### Sequenced Collections (JEP 431)

Uniform API for ordered collections.

Before:

```java
var first = list.get(0);
var last = list.get(list.size() - 1);
var reversed = new ArrayList<>(list);
Collections.reverse(reversed);
```

After:

```java
var first = list.getFirst();
var last = list.getLast();
var reversed = list.reversed();
```

**Why**: Uniform API across List, Deque, SortedSet, etc.

### Unnamed Patterns (JEP 443)

Reduces noise from unused pattern variables.

Before:

```java
switch (employee) {
    case Salaried s -> System.out.println("Salary: " + s.salary());
    case Contractor c -> System.out.println("Contractor");  // c unused
    case Intern i -> System.out.println("Intern");          // i unused
}
```

After:

```java
switch (employee) {
    case Salaried s -> System.out.println("Salary: " + s.salary());
    case Contractor _, Intern _ -> System.out.println("Non-salaried");
}
```

**Why**: Clearer intent, combines similar cases.

## Java 25 Features

### Flexible Constructor Bodies (JEP 513)

Enables validation before super() call.

Before:

```java
class Employee extends Person {
    Employee(String name, int age) {
        super(name, age);  // Must call first, even if args invalid
        if (age < 18 || age > 67) {
            throw new IllegalArgumentException("Invalid working age: " + age);
        }
    }
}
```

After:

```java
class Employee extends Person {
    Employee(String name, int age) {
        if (age < 18 || age > 67) {
            throw new IllegalArgumentException("Invalid working age: " + age);
        }
        super(name, age);  // Validate first, then construct
    }
}
```

**Why**: Fail-fast validation, prevents wasted object construction.

### Module Import Declarations (JEP 511)

Single import for entire module.

Before:

```java
import java.util.Map;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.function.Function;
import java.util.function.Predicate;
```

After:

```java
import module java.base;
```

**Why**: Dramatically reduces import boilerplate for commonly used modules.

**Note**: Use judiciously. For focused classes, explicit imports may still be preferred for clarity.
