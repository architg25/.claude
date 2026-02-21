# Scio Integration

Patterns for using Decibel with Scio/Apache Beam pipelines.

## DecibelIO Read

**Use when**: Reading from Decibel in batch pipelines

```scala
import com.spotify.scio._
import com.spotify.decibel.scio.DecibelIO

object MyPipelineJob {
  def main(cmdlineArgs: Array[String]): Unit = {
    val (sc, args) = ContextAndArgs(cmdlineArgs)

    val records: SCollection[MyTableRow] = sc
      .read(DecibelIO.read[MyTableRow](
        projectId = "my-gcp-project",
        instanceId = "my-bigtable-instance",
        tableId = "my-table"
      ))

    // Process records...

    sc.run()
  }
}
```

## DecibelIO Write

**Use when**: Writing to Decibel from batch pipelines

```scala
import com.spotify.decibel.scio.DecibelIO

val records: SCollection[MyTableRow] = // ... source data

records.write(DecibelIO.write[MyTableRow](
  projectId = "my-gcp-project",
  instanceId = "my-bigtable-instance",
  tableId = "my-table"
))
```

## Filtered Reads

### Partition Key Filter

**Use when**: Reading specific partitions

```scala
val userRecords = sc.read(DecibelIO.read[UserDataRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "user-data"
).withPartitionKeyFilter(PartitionKeyFilter.prefix("user-")))
```

### Row Key Range

**Use when**: Reading a range of rows

```scala
val recentRecords = sc.read(DecibelIO.read[EventRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "events"
).withRowKeyRange(
  startKey = "2024-01-01",
  endKey = "2024-12-31"
))
```

## Batch Writing Patterns

### Upsert Pattern

**Use when**: Insert or update rows

```scala
// Default write behavior is upsert
records.write(DecibelIO.write[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "my-table"
))
```

### Delete Pattern

**Use when**: Removing rows from Decibel

```scala
import com.spotify.decibel.scio.DecibelIO.Delete

keysToDelete
  .map(key => Delete(partitionKey = key))
  .write(DecibelIO.delete(
    projectId = "my-project",
    instanceId = "my-instance",
    tableId = "my-table"
  ))
```

## Performance Tuning

### Parallelism

**Use when**: Optimizing throughput

```scala
records.write(DecibelIO.write[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "my-table"
).withNumMutatePartitions(100))  // Increase write parallelism
```

### Batching

**Use when**: Reducing RPC overhead

```scala
records.write(DecibelIO.write[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "my-table"
).withBatchSize(1000))  // Batch mutations together
```

## Testing with Scio

### JobTest Pattern

**Use when**: Unit testing Decibel pipelines

```scala
import com.spotify.scio.testing._
import com.spotify.decibel.scio.DecibelIO

class MyPipelineJobTest extends PipelineSpec {
  "MyPipelineJob" should "process Decibel data" in {
    val inputData = Seq(
      MyTableRow("key1", "value1"),
      MyTableRow("key2", "value2")
    )

    JobTest[MyPipelineJob.type]
      .args(
        "--project=test-project",
        "--instance=test-instance"
      )
      .input(DecibelIO.read[MyTableRow](
        projectId = "test-project",
        instanceId = "test-instance",
        tableId = "test-table"
      ), inputData)
      .output(SomeIO("output"))(output => {
        output should haveSize(2)
      })
      .run()
  }
}
```

## Common Integration Patterns

### Decibel to BigQuery

**Use when**: Exporting Decibel data for analytics

```scala
val decibelData = sc.read(DecibelIO.read[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "my-table"
))

decibelData
  .map(row => convertToBigQueryRow(row))
  .saveAsBigQueryTable(
    "my-project:dataset.table",
    schema = mySchema,
    writeDisposition = WriteDisposition.WRITE_TRUNCATE
  )
```

### BigQuery to Decibel

**Use when**: Loading analytical results into Decibel

```scala
val bqData = sc.bigQueryTable("my-project:dataset.table")

bqData
  .map(row => convertToDecibelRow(row))
  .write(DecibelIO.write[MyRow](
    projectId = "my-project",
    instanceId = "my-instance",
    tableId = "my-table"
  ))
```

## Anti-Patterns

### Avoid: Reading Entire Table

Before (avoid):
```scala
// Full table scan - expensive!
val allData = sc.read(DecibelIO.read[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "large-table"
))
```

After:
```scala
// Use partition filter or row range
val filteredData = sc.read(DecibelIO.read[MyRow](
  projectId = "my-project",
  instanceId = "my-instance",
  tableId = "large-table"
).withPartitionKeyFilter(
  PartitionKeyFilter.range("2024-01", "2024-02")
))
```

### Avoid: Small Batches

Before (avoid):
```scala
records.write(DecibelIO.write[MyRow](...)
  .withBatchSize(10))  // Too small, high RPC overhead
```

After:
```scala
records.write(DecibelIO.write[MyRow](...)
  .withBatchSize(500))  // Better batching
```
