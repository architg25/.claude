# Testing Patterns

## Static Imports

### Pattern: Test Fixtures

Before:
```java
import com.example.TestFixtures;

class UserServiceTest {
    @Test
    void shouldCreateUser() {
        User user = TestFixtures.createUser("test");
        Address address = TestFixtures.createAddress("NYC");
        Order order = TestFixtures.createOrder(user);
    }
}
```

After:
```java
import static com.example.TestFixtures.*;

class UserServiceTest {
    @Test
    void shouldCreateUser() {
        User user = createUser("test");
        Address address = createAddress("NYC");
        Order order = createOrder(user);
    }
}
```

### Pattern: Assertion Libraries

Before:
```java
import org.assertj.core.api.Assertions;

@Test
void shouldFindUser() {
    User user = service.findById(1L);
    Assertions.assertThat(user).isNotNull();
    Assertions.assertThat(user.getName()).isEqualTo("John");
}
```

After:
```java
import static org.assertj.core.api.Assertions.*;

@Test
void shouldFindUser() {
    User user = service.findById(1L);
    assertThat(user).isNotNull();
    assertThat(user.getName()).isEqualTo("John");
}
```

### Pattern: Mockito

Before:
```java
import org.mockito.Mockito;

@Test
void shouldCallRepository() {
    Mockito.when(repository.findById(1L)).thenReturn(Optional.of(user));
    service.getUser(1L);
    Mockito.verify(repository).findById(1L);
}
```

After:
```java
import static org.mockito.Mockito.*;

@Test
void shouldCallRepository() {
    when(repository.findById(1L)).thenReturn(Optional.of(user));
    service.getUser(1L);
    verify(repository).findById(1L);
}
```

## Test Method Naming

### Pattern: Descriptive Test Names

Before:
```java
@Test
void test1() { ... }

@Test
void testFindUser() { ... }

@Test
void findUserReturnsNull() { ... }
```

After:
```java
@Test
void shouldReturnUserWhenIdExists() { ... }

@Test
void shouldThrowNotFoundExceptionWhenIdDoesNotExist() { ... }

@Test
void shouldReturnEmptyListWhenNoUsersMatch() { ... }
```

**Pattern**: `should[ExpectedBehavior]When[Condition]`

### Pattern: Context-Specific Test Names

Include specific context about WHERE the behavior occurs.

Before:
```java
@Test
void shouldAddFilterWhenVideoOnlyIsTrue() { ... }  // Filter where?

@Test
void shouldReturnEmptyWhenClientFails() { ... }    // Empty what? Which client?
```

After:
```java
@Test
void shouldAddVideoFilterToHermesUrlWhenVideoOnlyIsTrue() { ... }

@Test
void shouldReturnEmptyTrackListWhenSearchClientFailsRequest() { ... }
```

**Pattern elements**:
- Include target location: `ToUrl`, `InRequest`, `ToDatabase`, `InResponseBody`
- Include specific types: `EmptyList`, `NullUser`, `ZeroCount`
- Include specific actors: `SearchClient`, `PaymentGateway`, `UserRepository`

### Pattern: Align Assertions with Test Name

Test assertions must verify exactly what the test name promises.

Before (misaligned):
```java
@Test
void shouldAddVideoFilterToHermesUrlWhenVideoOnlyIsTrue() {
    // Given
    when(hermesClient.getPayload(any(), any(), any())).thenReturn(response);

    // When
    List<Track> result = service.search(query, videoOnly=true);

    // Then - WRONG: tests response, not URL construction!
    assertThat(result.size()).isEqualTo(1);
    assertThat(result.get(0).uri()).isEqualTo("spotify:track:123");
}
```

After (aligned):
```java
@Test
void shouldAddVideoFilterToHermesUrlWhenVideoOnlyIsTrue() {
    // Given
    ArgumentCaptor<String> urlCaptor = ArgumentCaptor.forClass(String.class);
    when(hermesClient.getPayload(any(), any(), any())).thenReturn(response);

    // When
    service.search(query, videoOnly=true);

    // Then - CORRECT: verifies URL contains the filter
    verify(hermesClient).getPayload(any(), any(), urlCaptor.capture());
    assertThat(urlCaptor.getValue()).contains("&track-type=video");
}
```

**Why**: If the test name says "ToUrl", assertions must verify URL content. Testing side effects not mentioned in the name creates confusion and maintenance burden.

## Test Structure

### Pattern: Given-When-Then / Arrange-Act-Assert

Before:
```java
@Test
void testUserCreation() {
    User user = new User("John", "john@example.com");
    user.setActive(true);
    UserResponse response = service.createUser(user);
    assertThat(response.getId()).isNotNull();
    assertThat(response.isActive()).isTrue();
    verify(repository).save(any());
    verify(emailService).sendWelcome(any());
}
```

After:
```java
@Test
void shouldCreateActiveUserAndSendWelcomeEmail() {
    // Given
    User user = createUser("John", "john@example.com");
    user.setActive(true);

    // When
    UserResponse response = service.createUser(user);

    // Then
    assertThat(response.getId()).isNotNull();
    assertThat(response.isActive()).isTrue();
    verify(repository).save(any());
    verify(emailService).sendWelcome(any());
}
```

## Single Assertion Focus

### Pattern: One Logical Concept Per Test

Before:
```java
@Test
void testUserOperations() {
    // Test creation
    User user = service.create("John");
    assertThat(user).isNotNull();

    // Test update
    user.setName("Jane");
    User updated = service.update(user);
    assertThat(updated.getName()).isEqualTo("Jane");

    // Test delete
    service.delete(user.getId());
    assertThat(service.findById(user.getId())).isEmpty();
}
```

After:
```java
@Test
void shouldCreateUserWithName() {
    User user = service.create("John");
    assertThat(user).isNotNull();
    assertThat(user.getName()).isEqualTo("John");
}

@Test
void shouldUpdateUserName() {
    User user = createUser("John");
    user.setName("Jane");

    User updated = service.update(user);

    assertThat(updated.getName()).isEqualTo("Jane");
}

@Test
void shouldDeleteUser() {
    User user = createUser("John");

    service.delete(user.getId());

    assertThat(service.findById(user.getId())).isEmpty();
}
```

## Parameterized Tests

### Pattern: Replace Duplicated Tests with @ParameterizedTest

Before:
```java
@Test
void shouldValidateEmailWithAtSymbol() {
    assertThat(validator.isValid("user@example.com")).isTrue();
}

@Test
void shouldRejectEmailWithoutAtSymbol() {
    assertThat(validator.isValid("userexample.com")).isFalse();
}

@Test
void shouldRejectEmptyEmail() {
    assertThat(validator.isValid("")).isFalse();
}

@Test
void shouldRejectNullEmail() {
    assertThat(validator.isValid(null)).isFalse();
}
```

After:
```java
@ParameterizedTest
@CsvSource({
    "user@example.com, true",
    "admin@test.org, true",
    "userexample.com, false",
    "'', false"
})
void shouldValidateEmail(String email, boolean expected) {
    assertThat(validator.isValid(email)).isEqualTo(expected);
}

@ParameterizedTest
@NullSource
@EmptySource
void shouldRejectInvalidEmail(String email) {
    assertThat(validator.isValid(email)).isFalse();
}
```

### Pattern: @ValueSource for Simple Values

Before:
```java
@Test
void shouldRejectNegativeAge() {
    assertThatThrownBy(() -> new Person("John", -1))
        .isInstanceOf(IllegalArgumentException.class);
}

@Test
void shouldRejectZeroAge() {
    assertThatThrownBy(() -> new Person("John", 0))
        .isInstanceOf(IllegalArgumentException.class);
}

@Test
void shouldRejectAgeOver150() {
    assertThatThrownBy(() -> new Person("John", 151))
        .isInstanceOf(IllegalArgumentException.class);
}
```

After:
```java
@ParameterizedTest
@ValueSource(ints = {-1, 0, 151, 200, -100})
void shouldRejectInvalidAge(int invalidAge) {
    assertThatThrownBy(() -> new Person("John", invalidAge))
        .isInstanceOf(IllegalArgumentException.class);
}
```

### Pattern: @MethodSource for Complex Test Data

Before:
```java
@Test
void shouldCalculateTaxForLowIncome() {
    assertThat(calculator.calculateTax(10000)).isEqualTo(1000);
}

@Test
void shouldCalculateTaxForMediumIncome() {
    assertThat(calculator.calculateTax(50000)).isEqualTo(7500);
}

@Test
void shouldCalculateTaxForHighIncome() {
    assertThat(calculator.calculateTax(100000)).isEqualTo(25000);
}
```

After:
```java
import static org.junit.jupiter.params.provider.Arguments.arguments;

@ParameterizedTest
@MethodSource("taxTestCases")
void shouldCalculateTax(int income, int expectedTax) {
    assertThat(calculator.calculateTax(income)).isEqualTo(expectedTax);
}

private static Stream<Arguments> taxTestCases() {
    return Stream.of(
        arguments(10000, 1000),
        arguments(50000, 7500),
        arguments(100000, 25000),
        arguments(0, 0)
    );
}
```

### Pattern: @EnumSource for Enum Testing

Before:
```java
@Test
void shouldHandlePendingStatus() {
    Order order = createOrder(OrderStatus.PENDING);
    assertThat(processor.canProcess(order)).isTrue();
}

@Test
void shouldHandleConfirmedStatus() {
    Order order = createOrder(OrderStatus.CONFIRMED);
    assertThat(processor.canProcess(order)).isTrue();
}

@Test
void shouldHandleShippedStatus() {
    Order order = createOrder(OrderStatus.SHIPPED);
    assertThat(processor.canProcess(order)).isTrue();
}
```

After:
```java
@ParameterizedTest
@EnumSource(value = OrderStatus.class, names = {"PENDING", "CONFIRMED", "SHIPPED"})
void shouldProcessActiveStatuses(OrderStatus status) {
    Order order = createOrder(status);
    assertThat(processor.canProcess(order)).isTrue();
}

@ParameterizedTest
@EnumSource(value = OrderStatus.class, mode = Mode.EXCLUDE, names = {"CANCELLED", "REFUNDED"})
void shouldProcessNonTerminalStatuses(OrderStatus status) {
    Order order = createOrder(status);
    assertThat(processor.canProcess(order)).isTrue();
}
```

## Exception Testing

### Pattern: Try-Catch to AssertJ

Before:
```java
@Test
void shouldThrowExceptionForInvalidId() {
    try {
        service.findById(-1L);
        fail("Expected exception was not thrown");
    } catch (IllegalArgumentException e) {
        assertThat(e.getMessage()).isEqualTo("ID must be positive");
    }
}
```

After:
```java
@Test
void shouldThrowExceptionForInvalidId() {
    assertThatThrownBy(() -> service.findById(-1L))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessage("ID must be positive");
}
```

### Pattern: Fluent Exception Chains

Before:
```java
@Test
void shouldThrowNotFoundWithDetails() {
    assertThatThrownBy(() -> service.findById(-1L))
        .isInstanceOf(IllegalArgumentException.class);
    // Separate assertions for message content
}
```

After:
```java
@Test
void shouldThrowNotFoundWithDetails() {
    assertThatThrownBy(() -> service.findById(-1L))
        .isInstanceOf(IllegalArgumentException.class)
        .hasMessageContaining("ID")
        .hasMessageContaining("-1")
        .hasNoCause();
}
```

### Pattern: Exception with Cause

Before:
```java
@Test
void shouldWrapDatabaseException() {
    assertThatThrownBy(() -> service.save(user))
        .isInstanceOf(ServiceException.class);
    // Can't easily verify the cause
}
```

After:
```java
@Test
void shouldWrapDatabaseException() {
    assertThatThrownBy(() -> service.save(user))
        .isInstanceOf(ServiceException.class)
        .hasMessage("Failed to save user")
        .hasCauseInstanceOf(SQLException.class)
        .hasRootCauseMessage("Connection refused");
}
```

## Nested Tests

### Pattern: @Nested for Test Organization

Before:
```java
class UserServiceTest {
    @Test
    void createShouldSaveUser() { ... }

    @Test
    void createShouldThrowForDuplicateEmail() { ... }

    @Test
    void createShouldSendWelcomeEmail() { ... }

    @Test
    void deleteShouldRemoveUser() { ... }

    @Test
    void deleteShouldThrowForNonExistentUser() { ... }

    @Test
    void updateShouldModifyUser() { ... }
}
```

After:
```java
class UserServiceTest {

    @Nested
    class Create {
        @Test
        void shouldSaveUser() { ... }

        @Test
        void shouldThrowForDuplicateEmail() { ... }

        @Test
        void shouldSendWelcomeEmail() { ... }
    }

    @Nested
    class Delete {
        @Test
        void shouldRemoveUser() { ... }

        @Test
        void shouldThrowForNonExistentUser() { ... }
    }

    @Nested
    class Update {
        @Test
        void shouldModifyUser() { ... }
    }
}
```

**Why**: Better organization, shared setup per group, clearer test output hierarchy.

## Fluent Assertion Chains

### Pattern: Chain Multiple Assertions

Before:
```java
@Test
void shouldCreateUserWithDefaults() {
    User user = service.create("John");

    assertThat(user).isNotNull();
    assertThat(user.getId()).isNotNull();
    assertThat(user.getName()).isEqualTo("John");
    assertThat(user.isActive()).isTrue();
    assertThat(user.getRoles()).contains(Role.USER);
}
```

After:
```java
import static org.assertj.core.api.Assertions.*;

@Test
void shouldCreateUserWithDefaults() {
    User user = service.create("John");

    assertThat(user)
        .isNotNull()
        .satisfies(u -> {
            assertThat(u.getId()).isNotNull();
            assertThat(u.getName()).isEqualTo("John");
            assertThat(u.isActive()).isTrue();
            assertThat(u.getRoles()).contains(Role.USER);
        });
}
```

### Pattern: Object Field Assertions

Before:
```java
@Test
void shouldMapUserToDto() {
    UserDto dto = mapper.toDto(user);

    assertThat(dto.getId()).isEqualTo(user.getId());
    assertThat(dto.getName()).isEqualTo(user.getName());
    assertThat(dto.getEmail()).isEqualTo(user.getEmail());
}
```

After:
```java
@Test
void shouldMapUserToDto() {
    UserDto dto = mapper.toDto(user);

    assertThat(dto)
        .extracting(UserDto::getId, UserDto::getName, UserDto::getEmail)
        .containsExactly(user.getId(), user.getName(), user.getEmail());
}
```

## Soft Assertions

### Pattern: Continue After First Failure

Before:
```java
@Test
void shouldHaveCorrectUserProperties() {
    User user = service.findById(1L);

    // If first assertion fails, remaining assertions don't run
    assertThat(user.getName()).isEqualTo("John");
    assertThat(user.getEmail()).isEqualTo("john@example.com");
    assertThat(user.getAge()).isEqualTo(30);
    assertThat(user.isActive()).isTrue();
}
```

After:
```java
@Test
void shouldHaveCorrectUserProperties() {
    User user = service.findById(1L);

    SoftAssertions.assertSoftly(softly -> {
        softly.assertThat(user.getName()).isEqualTo("John");
        softly.assertThat(user.getEmail()).isEqualTo("john@example.com");
        softly.assertThat(user.getAge()).isEqualTo(30);
        softly.assertThat(user.isActive()).isTrue();
    });
}
```

**Why**: All assertions run even if some fail, giving complete failure information in one test run.

## Test Data Builders

### Pattern: Builder for Complex Test Fixtures

Before:
```java
@Test
void shouldProcessOrder() {
    User user = new User();
    user.setId(1L);
    user.setName("John");
    user.setEmail("john@example.com");
    user.setActive(true);

    Address address = new Address();
    address.setStreet("123 Main St");
    address.setCity("NYC");
    address.setZipCode("10001");

    Order order = new Order();
    order.setUser(user);
    order.setShippingAddress(address);
    order.setStatus(OrderStatus.PENDING);
    order.setItems(List.of(new OrderItem("Widget", 2, 9.99)));

    OrderResult result = processor.process(order);

    assertThat(result.isSuccess()).isTrue();
}
```

After:
```java
import static com.example.TestBuilders.*;
import static org.assertj.core.api.Assertions.*;

@Test
void shouldProcessOrder() {
    Order order = anOrder()
        .withUser(aUser().withName("John").build())
        .withShippingAddress(anAddress().inCity("NYC").build())
        .withStatus(OrderStatus.PENDING)
        .withItem("Widget", 2, 9.99)
        .build();

    OrderResult result = processor.process(order);

    assertThat(result.isSuccess()).isTrue();
}
```

**Why**: Readable, reusable, and only specifies what's relevant to the test. Static imports make builder methods available without qualifiers.

## Argument Captors

### Pattern: Capture and Assert on Mock Arguments

Before:
```java
@Test
void shouldSendCorrectEmail() {
    service.registerUser("John", "john@example.com");

    verify(emailService).send(any(), any(), any());
    // Can't verify the actual email content!
}
```

After:
```java
import static org.mockito.Mockito.*;
import static org.assertj.core.api.Assertions.*;

@Test
void shouldSendCorrectEmail() {
    service.registerUser("John", "john@example.com");

    ArgumentCaptor<Email> emailCaptor = ArgumentCaptor.forClass(Email.class);
    verify(emailService).send(emailCaptor.capture());

    Email sentEmail = emailCaptor.getValue();
    assertThat(sentEmail.getTo()).isEqualTo("john@example.com");
    assertThat(sentEmail.getSubject()).contains("Welcome");
    assertThat(sentEmail.getBody()).contains("John");
}
```
