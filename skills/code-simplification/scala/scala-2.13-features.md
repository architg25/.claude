# Scala 2.13 Features

Modern Scala 2.13 features for cleaner, more expressive code.

## Option.when and Option.unless

### Option.when vs If-Some-None

Before:

```scala
if (condition) Some(value) else None
```

After:

```scala
Option.when(condition)(value)
```

### Option.unless (Inverse Condition)

Before:

```scala
if (!condition) Some(value) else None
```

After:

```scala
Option.unless(condition)(value)
```

### Real-World Example

Before:

```scala
def getUserRole(user: User): Option[Role] = {
  if (user.isActive && user.hasPermission) {
    Some(Role.Admin)
  } else {
    None
  }
}
```

After:

```scala
def getUserRole(user: User): Option[Role] = {
  Option.when(user.isActive && user.hasPermission)(Role.Admin)
}
```

## LazyList (Replaces Stream)

### LazyList vs Stream

Before (deprecated):

```scala
def fibonacciStream: Stream[BigInt] = {
  def loop(a: BigInt, b: BigInt): Stream[BigInt] =
    a #:: loop(b, a + b)
  loop(0, 1)
}
```

After:

```scala
def fibonacciList: LazyList[BigInt] = {
  def loop(a: BigInt, b: BigInt): LazyList[BigInt] =
    a #:: loop(b, a + b)
  loop(0, 1)
}
```

### Infinite Sequences

Before:

```scala
val naturals = Stream.from(1)  // Deprecated
```

After:

```scala
val naturals = LazyList.from(1)
```

### LazyList.unfold

Before:

```scala
def pageResults(start: Int): LazyList[Page] = {
  val page = fetchPage(start)
  if (page.isEmpty) LazyList.empty
  else page #:: pageResults(start + 1)
}
```

After:

```scala
val pages = LazyList.unfold(0) { offset =>
  val page = fetchPage(offset)
  Option.when(page.nonEmpty)((page, offset + 1))
}
```

## Tap and Pipe

### tap for Side Effects

Before:

```scala
val result = transform(data)
logger.debug(s"Transformed: $result")
process(result)
```

After:

```scala
import scala.util.chaining._

transform(data)
  .tap(r => logger.debug(s"Transformed: $r"))
  .pipe(process)
```

### pipe for Chaining

Before:

```scala
val step1 = transform(data)
val step2 = validate(step1)
val step3 = save(step2)
```

After:

```scala
import scala.util.chaining._

data
  .pipe(transform)
  .pipe(validate)
  .pipe(save)
```

### Real-World Example with Debugging

Before:

```scala
def processOrder(order: Order): Result = {
  val validated = validateOrder(order)
  println(s"Validated: $validated")
  val priced = calculatePricing(validated)
  println(s"Priced: $priced")
  val saved = saveOrder(priced)
  println(s"Saved: $saved")
  saved
}
```

After:

```scala
import scala.util.chaining._

def processOrder(order: Order): Result = {
  order
    .pipe(validateOrder)
    .tap(v => logger.debug(s"Validated: $v"))
    .pipe(calculatePricing)
    .tap(p => logger.debug(s"Priced: $p"))
    .pipe(saveOrder)
    .tap(s => logger.debug(s"Saved: $s"))
}
```

## Collection Improvements

### groupMapReduce (Single Pass)

Before:

```scala
// Two passes: group then map
data.groupBy(_.category)
    .map { case (k, v) => k -> v.map(_.value).sum }
```

After:

```scala
// Single pass
data.groupMapReduce(_.category)(_.value)(_ + _)
```

### partitionMap (Split by Either)

Before:

```scala
val results = items.map(validate)
val successes = results.collect { case Right(v) => v }
val failures = results.collect { case Left(e) => e }
```

After:

```scala
val (failures, successes) = items.map(validate).partitionMap(identity)
```

### minByOption and maxByOption

Before:

```scala
if (items.nonEmpty) Some(items.minBy(_.value)) else None
```

After:

```scala
items.minByOption(_.value)
```

### distinctBy

Before:

```scala
items.groupBy(_.key).values.map(_.head).toSeq
```

After:

```scala
items.distinctBy(_.key)
```

### sizeIs and lengthIs

Before:

```scala
if (list.size > 10) ...
// Inefficient for linked lists - traverses whole list
```

After:

```scala
if (list.sizeIs > 10) ...
// Short-circuits after 11 elements
```

## String Interpolation Improvements

### s, f, and raw Interpolators

```scala
// Standard interpolation
val greeting = s"Hello, $name"

// Formatted interpolation (printf-style)
val formatted = f"Value: $value%.2f"

// Raw interpolation (no escape processing)
val regex = raw"\d+\.\d+"
```

### Custom Interpolators with StringContext

Before:

```scala
def buildQuery(table: String, column: String): String = {
  s"SELECT * FROM $table WHERE $column = ?"  // SQL injection risk!
}
```

After:

```scala
implicit class SqlInterpolator(val sc: StringContext) extends AnyVal {
  def sql(args: Any*): SafeQuery = {
    val parts = sc.parts.iterator
    val params = args.iterator
    SafeQuery(parts.mkString("?"), args.toList)
  }
}

val query = sql"SELECT * FROM $table WHERE $column = $value"
```

## Using (Resource Management)

### Using for AutoCloseable Resources

Before:

```scala
val reader = new BufferedReader(new FileReader(file))
try {
  reader.lines().toArray.mkString("\n")
} finally {
  reader.close()
}
```

After:

```scala
import scala.util.Using

Using(new BufferedReader(new FileReader(file))) { reader =>
  reader.lines().toArray.mkString("\n")
}
```

### Multiple Resources

Before:

```scala
val reader = new BufferedReader(new FileReader(inFile))
try {
  val writer = new BufferedWriter(new FileWriter(outFile))
  try {
    // process
  } finally {
    writer.close()
  }
} finally {
  reader.close()
}
```

After:

```scala
import scala.util.Using

Using.Manager { use =>
  val reader = use(new BufferedReader(new FileReader(inFile)))
  val writer = use(new BufferedWriter(new FileWriter(outFile)))
  // process - both resources auto-closed
}
```

## Immutable Collections as Default

### Prefer Immutable by Default

```scala
// Scala 2.13 default imports point to immutable
val list = List(1, 2, 3)        // scala.collection.immutable.List
val map = Map("a" -> 1)         // scala.collection.immutable.Map
val set = Set(1, 2, 3)          // scala.collection.immutable.Set

// Explicitly use mutable when needed
import scala.collection.mutable
val buffer = mutable.ListBuffer[Int]()
```

### Converting Between Mutable and Immutable

Before:

```scala
val mutableList = mutable.ListBuffer(1, 2, 3)
val immutableList = mutableList.toList
```

After:

```scala
// 2.13 provides to(Factory) pattern
val mutableList = mutable.ListBuffer(1, 2, 3)
val immutableList = mutableList.to(List)
val immutableSet = mutableList.to(Set)
```

## View for Lazy Collections

### view for Lazy Transformations

Before:

```scala
// Creates intermediate collections
data.map(transform).filter(predicate).take(10)
```

After:

```scala
// Lazy - no intermediate collections
data.view.map(transform).filter(predicate).take(10).toList
```

### When to Use Views

```scala
// Good: multiple transformations, only need subset
data.view.map(heavyTransform).filter(predicate).headOption

// Not needed: single transformation
data.map(transform)

// Not needed: already lazy (Iterator, LazyList)
data.iterator.map(transform)
```
