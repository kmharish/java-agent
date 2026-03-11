---
name: testing
description: JUnit 5, Mockito, integration testing, and Testcontainers patterns
tools: [bash, read_file, write_file, edit_file]
---

# Java Testing Skill

## Test Organization

```
src/test/java/com/example/app/
├── controller/      # @WebMvcTest or @WebFluxTest
├── service/         # Unit tests with Mockito
├── repository/      # @DataJpaTest
├── integration/     # @SpringBootTest
└── util/            # Pure unit tests
```

## Unit Tests (JUnit 5 + Mockito)

```java
@ExtendWith(MockitoExtension.class)
class ItemServiceTest {

    @Mock
    private ItemRepository itemRepository;

    @InjectMocks
    private ItemService itemService;

    @Test
    void findById_existingItem_returnsItem() {
        // given
        var item = new Item(1L, "Test Item");
        when(itemRepository.findById(1L)).thenReturn(Optional.of(item));

        // when
        var result = itemService.findById(1L);

        // then
        assertThat(result).isNotNull();
        assertThat(result.getName()).isEqualTo("Test Item");
        verify(itemRepository).findById(1L);
    }

    @Test
    void findById_nonExistingItem_throwsException() {
        when(itemRepository.findById(99L)).thenReturn(Optional.empty());

        assertThatThrownBy(() -> itemService.findById(99L))
            .isInstanceOf(EntityNotFoundException.class)
            .hasMessageContaining("99");
    }
}
```

## Controller Tests

```java
@WebMvcTest(ItemController.class)
class ItemControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private ItemService itemService;

    @Test
    void getAll_returnsItems() throws Exception {
        when(itemService.findAll()).thenReturn(List.of(new ItemDTO(1L, "Test")));

        mockMvc.perform(get("/api/v1/items"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$[0].name").value("Test"));
    }
}
```

## Repository Tests

```java
@DataJpaTest
class ItemRepositoryTest {

    @Autowired
    private ItemRepository itemRepository;

    @Autowired
    private TestEntityManager entityManager;

    @Test
    void findByName_existingItem_returnsItem() {
        entityManager.persist(new Item(null, "Test Item"));
        entityManager.flush();

        var result = itemRepository.findByName("Test Item");

        assertThat(result).isPresent();
        assertThat(result.get().getName()).isEqualTo("Test Item");
    }
}
```

## Integration Tests

```java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class ItemIntegrationTest {

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void createAndRetrieveItem() {
        var request = new CreateItemRequest("New Item");
        var created = restTemplate.postForEntity("/api/v1/items", request, ItemDTO.class);

        assertThat(created.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(created.getBody().getName()).isEqualTo("New Item");
    }
}
```

## Testcontainers

```java
@SpringBootTest
@Testcontainers
class ItemRepositoryIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
        .withDatabaseName("testdb");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

## Testing Best Practices

1. **Name tests clearly**: `methodName_condition_expectedResult`
2. **Use AssertJ** over plain JUnit assertions — more readable
3. **One assertion concept per test** — test one behavior at a time
4. **Use given/when/then** structure (or arrange/act/assert)
5. **Don't test private methods** — test through the public API
6. **Mock external dependencies**, not the class under test
7. **Use `@Nested`** to group related tests
8. **Prefer `@MockitoBean`** over `@MockBean` (Spring Boot 3.4+)

## Running Tests

```bash
# All tests
./mvnw test

# Specific test class
./mvnw test -Dtest=ItemServiceTest

# Specific test method
./mvnw test -Dtest="ItemServiceTest#findById_existingItem_returnsItem"

# Integration tests only (if using failsafe plugin)
./mvnw verify -DskipUnitTests

# With coverage report
./mvnw test jacoco:report
# Report at: target/site/jacoco/index.html
```
