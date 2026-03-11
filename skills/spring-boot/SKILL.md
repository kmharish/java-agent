---
name: spring-boot
description: Spring Boot 3.x patterns, WebFlux, Security, JPA, and cloud-native development
tools: [bash, read_file, write_file, edit_file]
---

# Spring Boot Skill

## Project Structure Conventions

```
src/main/java/com/example/app/
├── config/          # @Configuration classes
├── controller/      # @RestController classes
├── service/         # @Service business logic
├── repository/      # @Repository / JPA interfaces
├── model/           # @Entity / DTOs
├── exception/       # Custom exceptions + @ControllerAdvice
├── security/        # Security config, filters
└── util/            # Utility classes
```

## Spring Boot 3.x Patterns

### REST Controllers
```java
@RestController
@RequestMapping("/api/v1/items")
@RequiredArgsConstructor
public class ItemController {
    private final ItemService itemService;

    @GetMapping
    public ResponseEntity<List<ItemDTO>> getAll() {
        return ResponseEntity.ok(itemService.findAll());
    }

    @PostMapping
    public ResponseEntity<ItemDTO> create(@Valid @RequestBody CreateItemRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
            .body(itemService.create(request));
    }
}
```

### Service Layer
- Use `@Service` annotation
- Inject dependencies via constructor (`@RequiredArgsConstructor` with Lombok, or explicit constructor)
- Keep business logic here, not in controllers
- Use `@Transactional` for operations that modify data

### JPA Best Practices
- Use `@Entity` with proper `@Table` annotations
- Always define `equals()` and `hashCode()` based on business keys, not `@Id`
- Prefer `FetchType.LAZY` for associations (default for `@OneToMany`, explicit for `@ManyToOne`)
- Use Spring Data JPA repository interfaces, not manual EntityManager unless needed
- Write custom queries with `@Query` annotation or query methods
- Avoid N+1 queries — use `@EntityGraph` or `JOIN FETCH` in JPQL

### Exception Handling
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(EntityNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleNotFound(EntityNotFoundException ex) {
        return ResponseEntity.status(HttpStatus.NOT_FOUND)
            .body(new ErrorResponse(ex.getMessage()));
    }
}
```

### Spring Security 6.x
```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/public/**").permitAll()
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth2 -> oauth2.jwt(Customizer.withDefaults()))
            .build();
    }
}
```

### Configuration
- Use `application.yml` over `application.properties`
- Use `@ConfigurationProperties` with `@EnableConfigurationProperties` for type-safe config
- Use profiles: `application-dev.yml`, `application-prod.yml`
- Never hardcode secrets — use environment variables or Spring Cloud Config

### WebFlux (Reactive)
- Use `Mono<T>` for single values, `Flux<T>` for streams
- Use `@RestController` with reactive return types
- Use `WebClient` instead of `RestTemplate` for HTTP calls
- Use `R2DBC` instead of JPA for reactive database access

## Common Patterns to Watch For

1. **Circular dependencies**: Refactor to break the cycle, don't use `@Lazy`
2. **Fat controllers**: Move logic to service layer
3. **Missing validation**: Add `@Valid` on request bodies, use Bean Validation annotations
4. **Exposed entities**: Use DTOs, never return JPA entities directly from controllers
5. **Missing error handling**: Add `@RestControllerAdvice` with proper error responses
6. **Hardcoded values**: Extract to `application.yml` and inject with `@Value` or `@ConfigurationProperties`
