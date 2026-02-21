# Dependency Injection

Dagger module patterns for ML clients.

## Salem Client Module

```java
import com.spotify.apollo.grpc.client.GrpcChannelFactory;
import com.spotify.salem.api.v1.Salem;
import dagger.Module;
import dagger.Provides;
import io.grpc.ManagedChannel;
import javax.inject.Named;
import javax.inject.Singleton;

@Module
public class SalemModule {
    private static final String PROBLEM_ID = "my-problem-id";

    @Provides
    @Singleton
    Salem.Client provideSalemClient(
            GrpcChannelFactory grpcChannelFactory,
            SourceEnvironment environment) {

        ManagedChannel channel = grpcChannelFactory
            .forTarget("nls://salem-api-" + PROBLEM_ID)
            .usePlaintext()
            .build();

        // Register for cleanup on shutdown
        environment.closer().register(channel::shutdown);

        return Salem.client(channel);
    }

    @Provides
    @Named("salemSlot")
    String provideSalemSlot(Config config) {
        return config.getString("salem.slot", "production");
    }

    @Provides
    @Named("salemProblemId")
    String provideSalemProblemId() {
        return PROBLEM_ID;
    }
}
```

## Fonzie Feature Reader Module

```java
import com.spotify.fonzie.BatchFeatureReader;
import com.spotify.fonzie.BatchFeatureReaderBuilder;
import com.spotify.fonzie.InitializingFeature;
import com.spotify.ml.jukebox.online.store.PartitionSelectionStrategy;
import dagger.Module;
import dagger.Provides;
import javax.inject.Singleton;
import java.util.List;
import java.util.concurrent.ExecutorService;

@Module
public class FonzieModule {

    @Provides
    @Singleton
    BatchFeatureReader provideBatchFeatureReader(
            ExecutorService executor,
            SourceEnvironment environment) {

        return BatchFeatureReaderBuilder.newBuilder()
            .executor(executor)
            .environment(environment)
            .initializingFeatures(getUserFeatures())
            .partitionSelectionStrategy(
                PartitionSelectionStrategy.PARTITION_SELECTION_STRATEGY_ALWAYS_LATEST)
            .build();
    }

    private List<InitializingFeature> getUserFeatures() {
        return List.of(
            InitializingFeature.of("/user/engagement/streams_30d", "streams30d"),
            InitializingFeature.of("/user/engagement/sessions_7d", "sessions7d"),
            InitializingFeature.of("/user/subscription/type", "subscriptionType"),
            InitializingFeature.of("/user/demographics/country", "country")
        );
    }
}
```

## Combined ML Module

```java
import dagger.Module;
import dagger.Provides;
import javax.inject.Singleton;

@Module(includes = {SalemModule.class, FonzieModule.class})
public class MLModule {

    @Provides
    @Singleton
    MLInferenceService provideMLInferenceService(
            BatchFeatureReader featureReader,
            Salem.Client salemClient,
            @Named("salemSlot") String slotName,
            @Named("salemProblemId") String problemId) {

        return new MLInferenceService(featureReader, salemClient, slotName, problemId);
    }
}
```

## Configurable Module

```java
@Module
public class ConfigurableSalemModule {

    @Provides
    @Singleton
    Salem.Client provideSalemClient(
            GrpcChannelFactory grpcChannelFactory,
            SourceEnvironment environment,
            Config config) {

        String problemId = config.getString("salem.problem-id");
        int timeoutMs = config.getInt("salem.timeout-ms", 100);

        ManagedChannel channel = grpcChannelFactory
            .forTarget("nls://salem-api-" + problemId)
            .usePlaintext()
            .defaultTimeout(Duration.ofMillis(timeoutMs))
            .build();

        environment.closer().register(channel::shutdown);

        return Salem.client(channel);
    }

    @Provides
    @Named("salemConfig")
    SalemConfig provideSalemConfig(Config config) {
        return new SalemConfig(
            config.getString("salem.problem-id"),
            config.getString("salem.slot", "production"),
            config.getInt("salem.timeout-ms", 100)
        );
    }
}
```

## Multiple Problem Support

```java
@Module
public class MultiProblemSalemModule {

    @Provides
    @Singleton
    @Named("classificationClient")
    Salem.Client provideClassificationClient(
            GrpcChannelFactory factory, SourceEnvironment env) {
        return createClient(factory, env, "user-classification");
    }

    @Provides
    @Singleton
    @Named("rankingClient")
    Salem.Client provideRankingClient(
            GrpcChannelFactory factory, SourceEnvironment env) {
        return createClient(factory, env, "content-ranking");
    }

    private Salem.Client createClient(
            GrpcChannelFactory factory, SourceEnvironment env, String problemId) {
        ManagedChannel channel = factory
            .forTarget("nls://salem-api-" + problemId)
            .usePlaintext()
            .build();

        env.closer().register(channel::shutdown);
        return Salem.client(channel);
    }
}
```

## Multiple Feature Reader Support

```java
@Module
public class MultiFonzieModule {

    @Provides
    @Singleton
    @Named("userFeatureReader")
    BatchFeatureReader provideUserFeatureReader(
            ExecutorService executor, SourceEnvironment environment) {
        return BatchFeatureReaderBuilder.newBuilder()
            .executor(executor)
            .environment(environment)
            .initializingFeatures(getUserFeatures())
            .build();
    }

    @Provides
    @Singleton
    @Named("itemFeatureReader")
    BatchFeatureReader provideItemFeatureReader(
            ExecutorService executor, SourceEnvironment environment) {
        return BatchFeatureReaderBuilder.newBuilder()
            .executor(executor)
            .environment(environment)
            .initializingFeatures(getItemFeatures())
            .build();
    }

    private List<InitializingFeature> getUserFeatures() {
        return List.of(
            InitializingFeature.of("/user/engagement/streams_30d", "streams30d")
        );
    }

    private List<InitializingFeature> getItemFeatures() {
        return List.of(
            InitializingFeature.of("/track/popularity/score", "popularity")
        );
    }
}
```

## Component Definition

```java
import dagger.Component;
import javax.inject.Singleton;

@Singleton
@Component(modules = {
    BaseModule.class,
    MLModule.class
})
public interface ServiceComponent {
    MLInferenceService mlInferenceService();
}
```

## Configuration Pattern

```hocon
# application.conf

salem {
  problem-id = "my-problem"
  slot = "production"
  timeout-ms = 100
}

fonzie {
  partition-strategy = "ALWAYS_LATEST"
}

grpc.client.endpoints {
  classification = "nls://salem-api-user-classification"
  ranking = "nls://salem-api-content-ranking"
}
```

## Related Patterns

- [Salem Client](salem-client.md) - Client setup
- [Fonzie Features](fonzie-features.md) - Feature reader setup
- [Testing](testing.md) - Mocking in tests
