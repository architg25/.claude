# Library Patterns

Common library idioms for Scala 2.13 at Spotify.

## Java Collection Converters

### Use scala.jdk.CollectionConverters

Before (deprecated):
```scala
import scala.collection.JavaConverters._  // Deprecated in 2.13
```

After:
```scala
import scala.jdk.CollectionConverters._
```

### Converting Java to Scala Collections

```scala
import scala.jdk.CollectionConverters._

val javaList: java.util.List[String] = ...
val scalaSeq: Seq[String] = javaList.asScala.toSeq

val javaMap: java.util.Map[String, Int] = ...
val scalaMap: Map[String, Int] = javaMap.asScala.toMap

val javaSet: java.util.Set[String] = ...
val scalaSet: Set[String] = javaSet.asScala.toSet
```

### Converting Scala to Java Collections

```scala
import scala.jdk.CollectionConverters._

val scalaList: List[String] = List("a", "b", "c")
val javaList: java.util.List[String] = scalaList.asJava

val scalaMap: Map[String, Int] = Map("a" -> 1)
val javaMap: java.util.Map[String, Int] = scalaMap.asJava
```

### Safe Iteration Pattern

Before:
```scala
// Risky - modifying underlying Java collection can cause issues
val javaList: java.util.List[String] = ...
javaList.asScala.foreach(process)
```

After:
```scala
// Safe - creates defensive copy
val javaList: java.util.List[String] = ...
javaList.asScala.toSeq.foreach(process)
```

## Algebird Semigroups and Monoids

> **See also**: For Scio-specific usage with `sumByKey` and pipeline aggregations, see
> [scio-patterns/aggregation-patterns.md](../scio-patterns/aggregation-patterns.md#semigroups-and-monoids)

### Implicit Semigroup Derivation

Before:
```scala
// Manual aggregation
case class Stats(count: Long, sum: Double, max: Double)

def combine(a: Stats, b: Stats): Stats = Stats(
  a.count + b.count,
  a.sum + b.sum,
  math.max(a.max, b.max)
)

data.reduce(combine)
```

After:
```scala
import com.twitter.algebird._
import com.spotify.scio.magnolify.auto._

case class Stats(count: Long, sum: Double, max: Double)

implicit val statsSemigroup: Semigroup[Stats] = Semigroup.gen[Stats]

data.sumByKey  // Uses implicit Semigroup
```

### Common Semigroup Patterns

```scala
import com.twitter.algebird._

// Numeric semigroups (addition)
implicit val longSg: Semigroup[Long] = Semigroup.longSemigroup
implicit val doubleSg: Semigroup[Double] = Semigroup.doubleSemigroup

// Max/Min semigroups
implicit def maxSg[T: Ordering]: Semigroup[Max[T]] = Max.maxSemigroup
implicit def minSg[T: Ordering]: Semigroup[Min[T]] = Min.minSemigroup

// Set union semigroup
implicit def setSg[T]: Semigroup[Set[T]] = Semigroup.setSemigroup

// First/Last value semigroups
implicit def firstSg[T]: Semigroup[First[T]] = First.firstSemigroup
implicit def lastSg[T]: Semigroup[Last[T]] = Last.lastSemigroup
```

### Monoid for Optional Identity

Before:
```scala
// Need to handle empty case
val result = if (data.isEmpty) Stats.empty else data.reduce(combine)
```

After:
```scala
import com.twitter.algebird.Monoid

implicit val statsMonoid: Monoid[Stats] = Monoid.gen[Stats]

// fold uses Monoid.zero for empty case
val result = data.fold
```

### HyperLogLog for Approximate Distinct Count

> **See also**: For Scio pipeline usage and decision criteria, see
> [scio-patterns/aggregation-patterns.md](../scio-patterns/aggregation-patterns.md#countapproxdistinct-with-hyperloglog)

Before:
```scala
// Exact distinct - memory intensive for large datasets
val distinctCount = data.map(_.userId).distinct.count
```

After:
```scala
import com.twitter.algebird.HyperLogLogMonoid

val hllMonoid = new HyperLogLogMonoid(12)  // 2^12 = 4096 buckets

val approximateCount = data
  .map(item => hllMonoid.create(item.userId.getBytes))
  .sum
  .approximateSize
  .estimate
```

### Bloom Filter for Set Membership

> **See also**: For Scio pipeline usage and decision criteria, see
> [scio-patterns/aggregation-patterns.md](../scio-patterns/aggregation-patterns.md#bloom-filter-for-set-membership)

```scala
import com.twitter.algebird.BloomFilter

// Create bloom filter
val bf = BloomFilter[String](numEntries = 1000000, fpProb = 0.01)

// Build from data
val filter = data.map(bf.create(_)).sum

// Check membership
if (filter.contains(item).isTrue) {
  // Might be in set (false positive possible)
}
```

## Magnolify Schema Derivation

### Automatic Case Class Mapping

Before:
```scala
// Manual Avro GenericRecord conversion
def fromGenericRecord(record: GenericRecord): MyRecord = {
  MyRecord(
    id = record.get("id").toString,
    value = record.get("value").asInstanceOf[Double],
    timestamp = record.get("timestamp").asInstanceOf[Long]
  )
}
```

After:
```scala
import magnolify.avro._

case class MyRecord(id: String, value: Double, timestamp: Long)

// Automatic derivation
val avroType = AvroType[MyRecord]
val record: MyRecord = avroType.from(genericRecord)
val genericRecord: GenericRecord = avroType.to(record)
```

### BigQuery Schema Derivation

```scala
import magnolify.bigquery._

case class Event(userId: String, eventType: String, timestamp: Instant)

// Automatic BigQuery table row conversion
val bqType = TableRowType[Event]
val event: Event = bqType.from(tableRow)
val tableRow: TableRow = bqType.to(event)
```

### Parquet Support

```scala
import magnolify.parquet._

case class TrackData(trackId: String, plays: Long, skips: Long)

val parquetType = ParquetType[TrackData]
```

### Handling Optional Fields

```scala
import magnolify.avro._

// Option fields map to nullable Avro fields
case class User(
  id: String,
  email: Option[String],
  age: Option[Int]
)

val avroType = AvroType[User]
```

## Cats Effect (IO)

### IO for Effectful Operations

Before:
```scala
// Side effects mixed with pure code
def processData(): Result = {
  val data = fetchFromDatabase()  // Side effect
  val transformed = transform(data)  // Pure
  saveToStorage(transformed)  // Side effect
  transformed
}
```

After:
```scala
import cats.effect.IO

def processData(): IO[Result] = {
  for {
    data        <- fetchFromDatabase()
    transformed <- IO.pure(transform(data))
    _           <- saveToStorage(transformed)
  } yield transformed
}
```

### Resource Management with Resource

```scala
import cats.effect.{IO, Resource}

val clientResource: Resource[IO, HttpClient] = Resource.make(
  acquire = IO(createClient())
)(
  release = client => IO(client.close())
)

// Use with guarantee of cleanup
clientResource.use { client =>
  client.fetch(url)
}
```

## ScalaTest Matchers

### Prefer Static Imports

Before:
```scala
class MyTest extends AnyFlatSpec {
  "result" should "be correct" in {
    val result = compute()
    assert(result == expected)
    assert(result.size == 3)
  }
}
```

After:
```scala
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class MyTest extends AnyFlatSpec with Matchers {
  "result" should "be correct" in {
    val result = compute()
    result shouldBe expected
    result should have size 3
  }
}
```

### Collection Matchers

```scala
import org.scalatest.matchers.should.Matchers._

result should contain(expected)
result should contain allOf("a", "b", "c")
result should contain oneOf("x", "y", "z")
result should contain noneOf("bad", "invalid")
result should have length 5
result shouldBe empty
result should not be empty
```

### Option and Either Matchers

```scala
import org.scalatest.matchers.should.Matchers._

maybeValue shouldBe defined
maybeValue shouldBe Some(expected)
maybeValue shouldBe None

eitherResult shouldBe a[Right[_, _]]
eitherResult shouldBe Left(error)
```

## Circe JSON

### Automatic Derivation

Before:
```scala
// Manual JSON parsing
def parseUser(json: String): User = {
  val parsed = JsonParser.parse(json)
  User(
    parsed.getString("name"),
    parsed.getInt("age")
  )
}
```

After:
```scala
import io.circe._
import io.circe.generic.auto._
import io.circe.parser._

case class User(name: String, age: Int)

// Automatic derivation
val result: Either[Error, User] = decode[User](jsonString)
```

### Semi-Automatic Derivation (More Control)

```scala
import io.circe._
import io.circe.generic.semiauto._

case class User(name: String, age: Int)

object User {
  implicit val decoder: Decoder[User] = deriveDecoder[User]
  implicit val encoder: Encoder[User] = deriveEncoder[User]
}
```

### Custom Field Names

```scala
import io.circe._
import io.circe.generic.extras.Configuration
import io.circe.generic.extras.semiauto._

implicit val config: Configuration = Configuration.default.withSnakeCaseMemberNames

case class UserProfile(firstName: String, lastName: String)
// Maps to/from: {"first_name": "...", "last_name": "..."}

implicit val decoder: Decoder[UserProfile] = deriveConfiguredDecoder
implicit val encoder: Encoder[UserProfile] = deriveConfiguredEncoder
```
