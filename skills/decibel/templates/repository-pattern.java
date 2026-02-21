package {{PACKAGE}};

import com.spotify.decibel.Connection;
import com.spotify.decibel.Table;
import com.spotify.decibel.Key;
import java.util.Optional;
import java.util.concurrent.CompletableFuture;

/**
 * Repository for {{TABLE_DESCRIPTION}}
 */
public class {{REPOSITORY_NAME}} {
    private final Table<{{ROW_TYPE}}> table;

    public {{REPOSITORY_NAME}}(Connection connection) {
        this.table = connection.table({{ROW_TYPE}}.class);
    }

    public CompletableFuture<Optional<{{ROW_TYPE}}>> get({{KEY_TYPE}} key) {
        return table.get(Key.of(key));
    }

    public CompletableFuture<Void> put({{ROW_TYPE}} row) {
        return table.put(row);
    }

    public CompletableFuture<Void> delete({{KEY_TYPE}} key) {
        return table.delete(Key.of(key));
    }
}
