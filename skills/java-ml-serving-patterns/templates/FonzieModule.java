package com.spotify.{{TEAM}}.{{PROJECT}}.dagger;

import com.spotify.apollo.environment.SourceEnvironment;
import com.spotify.fonzie.BatchFeatureReader;
import com.spotify.fonzie.BatchFeatureReaderBuilder;
import com.spotify.fonzie.InitializingFeature;
import com.spotify.ml.jukebox.online.store.PartitionSelectionStrategy;
import dagger.Module;
import dagger.Provides;
import javax.inject.Singleton;
import java.util.List;
import java.util.concurrent.ExecutorService;

/**
 * Dagger module for Fonzie feature reader configuration.
 *
 * Provides BatchFeatureReader for fetching features from Jukebox.
 */
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
            .initializingFeatures(getFeatures())
            .partitionSelectionStrategy(
                PartitionSelectionStrategy.PARTITION_SELECTION_STRATEGY_ALWAYS_LATEST)
            .build();
    }

    /**
     * Define the features to fetch from Jukebox.
     *
     * Feature paths must match exactly what's registered in Jukebox.
     * Aliases are used to reference features in code.
     */
    private List<InitializingFeature> getFeatures() {
        return List.of(
            // User engagement features
            InitializingFeature.of("{{FEATURE_PATH_1}}", "{{FEATURE_ALIAS_1}}"),
            InitializingFeature.of("{{FEATURE_PATH_2}}", "{{FEATURE_ALIAS_2}}"),

            // Add more features as needed:
            // InitializingFeature.of("/user/subscription/type", "subscriptionType"),
            // InitializingFeature.of("/user/demographics/country", "country"),
        );
    }
}
