package com.spotify.{{TEAM}}.{{PROJECT}}.dagger;

import com.spotify.apollo.grpc.client.GrpcChannelFactory;
import com.spotify.apollo.environment.SourceEnvironment;
import com.spotify.salem.api.v1.Salem;
import dagger.Module;
import dagger.Provides;
import io.grpc.ManagedChannel;
import javax.inject.Named;
import javax.inject.Singleton;

/**
 * Dagger module for Salem client configuration.
 *
 * Provides Salem gRPC client for problem: {{PROBLEM_ID}}
 */
@Module
public class SalemClientModule {
    private static final String PROBLEM_ID = "{{PROBLEM_ID}}";

    @Provides
    @Singleton
    Salem.Client provideSalemClient(
            GrpcChannelFactory grpcChannelFactory,
            SourceEnvironment environment) {

        // Create gRPC channel with NLS service discovery
        ManagedChannel channel = grpcChannelFactory
            .forTarget("nls://salem-api-" + PROBLEM_ID)
            .usePlaintext()  // Required for internal gRPC traffic
            .build();

        // Register channel for cleanup on service shutdown
        environment.closer().register(channel::shutdown);

        return Salem.client(channel);
    }

    @Provides
    @Named("salemProblemId")
    String provideSalemProblemId() {
        return PROBLEM_ID;
    }

    @Provides
    @Named("salemSlot")
    String provideSalemSlot() {
        // Configure via environment or config in production
        return System.getenv().getOrDefault("SALEM_SLOT", "{{DEFAULT_SLOT}}");
    }
}
