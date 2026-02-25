# Domain Agent Registry

Mapping of technical domains to their specialized expert agents. Use this registry to detect which domain experts to spawn based on patterns found in the content being analyzed.

## Domain-to-Agent Mapping

| Domain              | Pattern Signals                                                                                                                                                    | Expert Agent                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- |
| Flyte/Liftoff       | Flyte, Liftoff, workflow orchestration, `@workflow`, `@task`                                                                                                       | flyte-liftoff-expert                |
| Luigi               | Luigi, Styx, ice-luigi, `luigi.Task`, pipeline scheduling                                                                                                          | luigi-workflow-expert               |
| Scio/Beam           | Scio, SCollection, Beam, Apache Beam, pipeline, PCollection                                                                                                        | scio-pipeline-optimization-analyzer |
| Data Annotations    | `@BigQueryType`, `@description`, data annotations, GDPR, PII, `saveAsTypedParquetFile`, `ParquetType`, Avro schema, `.avsc`, `.proto` with `spotify.data.metadata` | data-annotation-reviewer            |
| Hendrix/ML          | Hendrix, Ray, ML training, model serving, feature store, ML platform                                                                                               | hendrix-expert                      |
| Backend Infra       | Decibel, Locus, caching, Bigtable, gRPC services, Apollo framework                                                                                                 | backend-infrastructure-expert       |
| Search/Indexing     | Vespa, search indexing, YQL, search ranking, index building                                                                                                        | search-indexing-expert              |
| RCS/Experimentation | RCS, experiments, feature flags, A/B testing, rollout, exposure                                                                                                    | experimentation-expert              |
| ML Serving          | Salem, ML serving, Fonzie, feature fetching, model inference                                                                                                       | java-ml-serving-expert              |

## How to Use

1. **Scan content** (RFC, ticket, codebase, changed files) for pattern signals from the table above
2. **Output detection results** showing which domains matched and which did not
3. **Spawn the corresponding expert agent** for each detected domain, in parallel with standard agents
4. **Include domain expert findings** in synthesis/review output

## Detection Output Format

```
## Domains Detected

Based on content analysis:
- [check] [Domain]: Found "[pattern]" -> Will spawn [agent-name]
- [cross] [Domain]: Not detected

[N] domain expert(s) will be included.
```
