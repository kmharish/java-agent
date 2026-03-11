---
name: code-review
description: SOLID principles, clean code, security review, and performance analysis for Java
tools: [bash, read_file, write_file, edit_file]
---

# Java Code Review Skill

## Review Checklist

### SOLID Principles

**Single Responsibility (SRP)**
- Each class has one reason to change
- Controllers only handle HTTP concerns
- Services contain business logic only
- Repositories handle data access only
- Watch for "God classes" with too many responsibilities

**Open/Closed (OCP)**
- Code is open for extension, closed for modification
- Use interfaces and strategy pattern instead of switch/if-else chains
- New behavior should be addable without changing existing code

**Liskov Substitution (LSP)**
- Subtypes must be substitutable for their base types
- Don't throw unexpected exceptions in overridden methods
- Don't strengthen preconditions or weaken postconditions

**Interface Segregation (ISP)**
- No client should depend on methods it doesn't use
- Prefer many small interfaces over one large one
- Split fat interfaces into focused ones

**Dependency Inversion (DIP)**
- Depend on abstractions, not concretions
- Inject interfaces, not implementations
- High-level modules shouldn't depend on low-level modules

### Clean Code

- **Method length**: Keep methods under ~20 lines. Extract helper methods.
- **Parameter count**: Max 3-4 params. Use parameter objects for more.
- **Naming**: Classes are nouns, methods are verbs. Be descriptive but concise.
- **Comments**: Code should be self-documenting. Comments explain *why*, not *what*.
- **Magic numbers**: Extract to named constants.
- **Null handling**: Use `Optional<T>` return types. Never return null from a method that could return Optional.
- **Exception handling**: Don't catch `Exception` or `Throwable` generically. Handle specific exceptions.

### Security Review

- **SQL Injection**: Use parameterized queries (JPA handles this). Never concatenate SQL strings.
- **XSS**: Sanitize output. Use appropriate content-type headers.
- **CSRF**: Enable CSRF protection for browser-facing endpoints.
- **Authentication**: Verify all endpoints require auth unless explicitly public.
- **Authorization**: Check @PreAuthorize or method-level security on sensitive operations.
- **Secrets**: No hardcoded passwords, API keys, or connection strings. Use env vars or vault.
- **Input validation**: `@Valid` on all request bodies. Validate path/query params.
- **Logging**: Never log sensitive data (passwords, tokens, PII).
- **Dependencies**: Check for known vulnerabilities with `./mvnw dependency-check:check`.

### Performance

- **N+1 queries**: Use `JOIN FETCH`, `@EntityGraph`, or batch fetching.
- **Missing indexes**: Check `@Index` on frequently queried columns.
- **Eager loading**: Default to `LAZY` fetch. Only use `EAGER` when justified.
- **Connection pools**: Configure HikariCP properly (pool size, timeouts).
- **Caching**: Use `@Cacheable` for expensive, rarely-changing operations.
- **Pagination**: Always paginate list endpoints. Use `Pageable` parameter.

## Review Output Format

When reviewing code, provide:

1. **Summary**: One-line assessment (looks good / needs work / has issues)
2. **Issues**: Categorized as Critical / Warning / Suggestion
3. **Good patterns**: Call out things done well
4. **Recommendations**: Concrete, actionable fixes with code examples
