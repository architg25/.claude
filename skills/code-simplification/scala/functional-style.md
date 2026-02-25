# Functional Style Patterns

Scala functional programming patterns for cleaner, more expressive code.

## Pattern Matching

### Type Matching vs isInstanceOf

Before:

```scala
def process(x: Any): String = {
  if (x.isInstanceOf[Int]) {
    val i = x.asInstanceOf[Int]
    s"number: ${i * 2}"
  } else if (x.isInstanceOf[String]) {
    val s = x.asInstanceOf[String]
    s"text: ${s.toUpperCase}"
  } else {
    "unknown"
  }
}
```

After:

```scala
def process(x: Any): String = x match {
  case i: Int    => s"number: ${i * 2}"
  case s: String => s"text: ${s.toUpperCase}"
  case _         => "unknown"
}
```

### Boolean Conditions as Match

Before:

```scala
def grade(score: Int): String = {
  if (score >= 90) "A"
  else if (score >= 80) "B"
  else if (score >= 70) "C"
  else if (score >= 60) "D"
  else "F"
}
```

After:

```scala
def grade(score: Int): String = score match {
  case s if s >= 90 => "A"
  case s if s >= 80 => "B"
  case s if s >= 70 => "C"
  case s if s >= 60 => "D"
  case _            => "F"
}
```

### Extractors and Destructuring

Before:

```scala
def processUser(user: User): String = {
  val name = user.name
  val age = user.age
  s"$name is $age years old"
}
```

After:

```scala
def processUser(user: User): String = user match {
  case User(name, age, _) => s"$name is $age years old"
}
```

## Option Handling

### Avoid getOrElse on Option.get

Before:

```scala
val value = if (option.isDefined) option.get else default
```

After:

```scala
val value = option.getOrElse(default)
```

### Option.map vs Pattern Matching

Before:

```scala
maybeUser match {
  case Some(user) => Some(user.name)
  case None       => None
}
```

After:

```scala
maybeUser.map(_.name)
```

### Option.flatMap for Chained Optionals

Before:

```scala
maybeUser match {
  case Some(user) => user.address match {
    case Some(address) => Some(address.city)
    case None          => None
  }
  case None => None
}
```

After:

```scala
maybeUser.flatMap(_.address).map(_.city)
```

### Option.fold vs match

Before:

```scala
maybeValue match {
  case Some(v) => process(v)
  case None    => defaultResult
}
```

After:

```scala
maybeValue.fold(defaultResult)(process)
```

## Either Handling

### Either.map and flatMap

Before:

```scala
result match {
  case Right(value) => Right(transform(value))
  case Left(error)  => Left(error)
}
```

After:

```scala
result.map(transform)
```

### Either.fold for Pattern Elimination

Before:

```scala
result match {
  case Right(value) => handleSuccess(value)
  case Left(error)  => handleError(error)
}
```

After:

```scala
result.fold(handleError, handleSuccess)
```

## Try Handling

### Try vs try-catch

Before:

```scala
val result = try {
  Some(riskyOperation())
} catch {
  case _: Exception => None
}
```

After:

```scala
val result = Try(riskyOperation()).toOption
```

### Try.recover for Error Handling

Before:

```scala
Try(parse(input)) match {
  case Success(value)              => value
  case Failure(_: ParseException)  => defaultValue
  case Failure(e)                  => throw e
}
```

After:

```scala
Try(parse(input)).recover {
  case _: ParseException => defaultValue
}.get
```

## For-Comprehensions

### Nested flatMap Chains

Before:

```scala
def getOrderTotal(userId: String): Option[Double] = {
  findUser(userId).flatMap { user =>
    findOrder(user.orderId).flatMap { order =>
      calculateDiscount(order).map { discount =>
        order.total - discount
      }
    }
  }
}
```

After:

```scala
def getOrderTotal(userId: String): Option[Double] = {
  for {
    user     <- findUser(userId)
    order    <- findOrder(user.orderId)
    discount <- calculateDiscount(order)
  } yield order.total - discount
}
```

### For-Comprehension with Guards

Before:

```scala
users.flatMap { user =>
  if (user.isActive) {
    orders.filter(_.userId == user.id).map { order =>
      (user.name, order.total)
    }
  } else {
    Seq.empty
  }
}
```

After:

```scala
for {
  user  <- users if user.isActive
  order <- orders if order.userId == user.id
} yield (user.name, order.total)
```

## Immutability

> **Note on Scio Pipelines**: While immutability is the default recommendation for Scala code,
> mutable state is acceptable _inside_ `aggregateByKey` operations for performance reasons.
> See [scio-patterns/aggregation-patterns.md](../scio-patterns/aggregation-patterns.md#mutable-aggregations)
> for details on when mutable state is appropriate in Scio contexts.

### Var to Val with Fold

Before:

```scala
var sum = 0
for (item <- items) {
  sum += item.value
}
```

After:

```scala
val sum = items.foldLeft(0)(_ + _.value)
// Or even simpler:
val sum = items.map(_.value).sum
```

### Mutable Collection to Immutable

Before:

```scala
val result = mutable.ListBuffer[String]()
for (item <- items) {
  if (item.isValid) {
    result += item.name
  }
}
result.toList
```

After:

```scala
items.filter(_.isValid).map(_.name)
```

### Copy Instead of Mutate

Before:

```scala
val user = new User()
user.name = "Alice"
user.age = 30
user
```

After:

```scala
User(name = "Alice", age = 30)
// Or for updates:
user.copy(name = "Alice", age = 30)
```

## Pure Functions

### Avoid Side Effects in Map

Before:

```scala
items.map { item =>
  println(s"Processing: $item")  // Side effect!
  process(item)
}
```

After:

```scala
// Separate logging from transformation
items.foreach(item => logger.debug(s"Processing: $item"))
items.map(process)

// Or use tap for debugging:
items.map(process).tap(results => logger.debug(s"Processed: $results"))
```

### Extract Impure Code

Before:

```scala
def processAndSave(data: Data): Unit = {
  val transformed = transform(data)  // Pure
  val validated = validate(transformed)  // Pure
  database.save(validated)  // Impure
  sendNotification(validated)  // Impure
}
```

After:

```scala
// Pure transformation
def process(data: Data): Either[Error, ValidData] = {
  for {
    transformed <- transform(data)
    validated   <- validate(transformed)
  } yield validated
}

// Impure effects separated
def saveAndNotify(data: ValidData): IO[Unit] = {
  database.save(data) *> sendNotification(data)
}
```

## Case Classes

### Use Case Classes for Data

Before:

```scala
class User(var name: String, var age: Int) {
  override def equals(other: Any): Boolean = other match {
    case that: User => name == that.name && age == that.age
    case _ => false
  }
  override def hashCode(): Int = (name, age).hashCode
  override def toString: String = s"User($name, $age)"
}
```

After:

```scala
case class User(name: String, age: Int)
// Equals, hashCode, toString, copy, pattern matching all included
```

### Companion Object Factory Methods

Before:

```scala
val user = new User("", 0)
user.name = name
user.age = age
```

After:

```scala
case class User(name: String, age: Int)

object User {
  def fromMap(data: Map[String, Any]): Option[User] = for {
    name <- data.get("name").collect { case s: String => s }
    age  <- data.get("age").collect { case i: Int => i }
  } yield User(name, age)
}
```
