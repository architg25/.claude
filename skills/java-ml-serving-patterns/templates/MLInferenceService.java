package com.spotify.{{TEAM}}.{{PROJECT}}.ml;

import com.spotify.apollo.RequestContext;
import com.spotify.fonzie.BatchFeatureReader;
import com.spotify.ml.jukebox.online.store.entity.EntityIdSet;
import com.spotify.salem.api.v1.*;
import io.grpc.Context;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import java.util.List;
import java.util.concurrent.CompletionStage;

import static com.spotify.ml.feature.v3.Identifier.IDENTIFIER_GID;
import static com.spotify.ml.feature.v3.PrimitiveEntity.PRIMITIVE_ENTITY_USER;

/**
 * ML inference service combining Fonzie feature fetching with Salem model serving.
 *
 * Usage:
 * <pre>
 * CompletionStage<{{MODEL_NAME}}Result> result = service.classify(context, userId);
 * </pre>
 */
@Singleton
public class {{MODEL_NAME}}InferenceService {
    private static final Logger log = LoggerFactory.getLogger({{MODEL_NAME}}InferenceService.class);
    private static final String SERVICE_NAME = "{{SERVICE_NAME}}";

    private final BatchFeatureReader featureReader;
    private final Salem.Client salemClient;
    private final Problem problem;
    private final Client clientId;

    @Inject
    public {{MODEL_NAME}}InferenceService(
            BatchFeatureReader featureReader,
            Salem.Client salemClient,
            @Named("salemProblemId") String problemId,
            @Named("salemSlot") String slotName) {

        this.featureReader = featureReader;
        this.salemClient = salemClient;

        this.problem = Problem.newBuilder()
            .setId(problemId)
            .setSlotName(slotName)
            .build();

        this.clientId = Client.newBuilder()
            .setId(SERVICE_NAME)
            .build();
    }

    /**
     * Classify a user using ML model.
     *
     * @param context Request context
     * @param userId User GID to classify
     * @return Classification result
     */
    public CompletionStage<{{MODEL_NAME}}Result> classify(Context context, String userId) {
        return fetchUserFeatures(context, userId)
            .thenCompose(features -> sendClassifyRequest(context, userId, features))
            .thenApply(this::parseResponse)
            .exceptionally(error -> {
                log.error("Classification failed for user {}", userId, error);
                return {{MODEL_NAME}}Result.unknown();
            });
    }

    private CompletionStage<FeatureSet> fetchUserFeatures(Context context, String userId) {
        EntityIdSet entity = EntityIdSet.of(PRIMITIVE_ENTITY_USER, IDENTIFIER_GID, userId);

        return featureReader.readBatch(context, List.of(entity))
            .itemFeatures()
            .thenApply(featureSets -> {
                if (featureSets.isEmpty()) {
                    throw new RuntimeException("No features found for user: " + userId);
                }
                return featureSets.get(0);
            });
    }

    private CompletionStage<ClassifyResponse> sendClassifyRequest(
            Context context, String userId, FeatureSet features) {

        ClassifyRequest request = ClassifyRequest.newBuilder()
            .setProblem(problem)
            .setClient(clientId)
            .setContext(RequestContext.newBuilder().setSpotifyUid(userId))
            .setFeatures(features)
            .build();

        return salemClient.classify(context, request);
    }

    private {{MODEL_NAME}}Result parseResponse(ClassifyResponse response) {
        Prediction prediction = response.getPrediction();
        return new {{MODEL_NAME}}Result(
            prediction.getClassIndex(),
            prediction.getProbability()
        );
    }

    /**
     * Result class for {{MODEL_NAME}} predictions.
     */
    public static class {{MODEL_NAME}}Result {
        private final int classIndex;
        private final float probability;

        public {{MODEL_NAME}}Result(int classIndex, float probability) {
            this.classIndex = classIndex;
            this.probability = probability;
        }

        public static {{MODEL_NAME}}Result unknown() {
            return new {{MODEL_NAME}}Result(-1, 0.0f);
        }

        public int getClassIndex() {
            return classIndex;
        }

        public float getProbability() {
            return probability;
        }

        public boolean isUnknown() {
            return classIndex == -1;
        }
    }
}
