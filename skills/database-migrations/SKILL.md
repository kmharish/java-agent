# Database Migrations Skill (Flyway + Liquibase)

Used in virtually every production Spring Boot project. Pick one tool per project — don't mix them.

---

## Flyway

### Dependencies

**Maven:**
```xml
<!-- Production -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
</dependency>
<!-- Required for MySQL 8+ -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-mysql</artifactId>
</dependency>
<!-- Required for SQL Server -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-sqlserver</artifactId>
</dependency>

<!-- Test isolation (Flyway test extensions) -->
<dependency>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-core</artifactId>
    <scope>test</scope>
</dependency>
```

**Gradle (Kotlin DSL):**
```kotlin
implementation("org.flywaydb:flyway-core")
implementation("org.flywaydb:flyway-mysql") // MySQL 8+

testImplementation("org.flywaydb:flyway-core")
```

Spring Boot auto-configures Flyway when `flyway-core` is on the classpath and a `DataSource` is available.

---

### File Naming Convention

```
src/main/resources/db/migration/
  V1__create_users_table.sql
  V2__add_email_index.sql
  V3__add_audit_columns.sql
  V3.1__backfill_audit_columns.sql   ← sub-versions allowed
  R__refresh_reporting_view.sql      ← repeatable (runs when checksum changes)
  U3__undo_audit_columns.sql         ← undo (Flyway Teams only)
```

**Rules:**
- `V` prefix = versioned migration (runs once)
- `R` prefix = repeatable migration (re-runs when file content changes)
- Double underscore `__` separates version from description
- Underscores in description become spaces in the history table
- Version numbers must be unique; gaps are fine
- Never modify a committed migration file — checksums will fail

---

### Configuration

```yaml
# application.yml
spring:
  flyway:
    enabled: true
    locations: classpath:db/migration
    baseline-on-migrate: false        # set true only for existing DBs without flyway history
    baseline-version: 0               # version to use as baseline
    out-of-order: false               # enforce strict ordering (keep false in prod)
    validate-on-migrate: true         # always validate checksums before running
    clean-disabled: true              # NEVER allow flyway:clean in production
    table: flyway_schema_history      # default history table name
    schemas: public                   # schemas to manage (PostgreSQL)
    default-schema: public
    placeholders:
      app_user: myapp                 # use ${app_user} in SQL files
```

**Per-environment overrides:**
```yaml
# application-test.yml
spring:
  flyway:
    clean-disabled: false             # allow clean in test environments
    out-of-order: true                # tolerate out-of-order in CI/CD parallel branches
```

---

### Baseline on Existing Databases

When adding Flyway to a database that already has tables:

1. Create `V1__baseline.sql` that is empty or a no-op (or skip it).
2. Set `baseline-on-migrate: true` and `baseline-version: 1` on first run only.
3. Flyway will mark V1 as applied without running it, then run V2+ normally.
4. **Revert `baseline-on-migrate: false` after first migration** — it's a one-time operation.

```bash
# Or use the CLI directly:
flyway -url=jdbc:postgresql://localhost/mydb \
       -user=postgres \
       -password=secret \
       baseline -baselineVersion=1 -baselineDescription="Existing schema"
```

---

### Repair Command

Use when a migration fails midway (e.g., syntax error in SQL):

```bash
# Fix the SQL, then repair to clear the failed entry from history:
flyway repair

# Spring Boot (via Maven plugin):
mvn flyway:repair -Dflyway.url=... -Dflyway.user=... -Dflyway.password=...
```

The `repair` command:
- Removes failed migration entries from the history table
- Realigns checksums for migrations that were changed (use sparingly)
- Does NOT undo the partial changes — fix those manually first

---

### Maven Plugin

```xml
<plugin>
    <groupId>org.flywaydb</groupId>
    <artifactId>flyway-maven-plugin</artifactId>
    <configuration>
        <url>${flyway.url}</url>
        <user>${flyway.user}</user>
        <password>${flyway.password}</password>
        <locations>
            <location>filesystem:src/main/resources/db/migration</location>
        </locations>
    </configuration>
</plugin>
```

Useful goals: `flyway:migrate`, `flyway:info`, `flyway:validate`, `flyway:repair`, `flyway:clean` (never in prod).

---

### Integration with @DataJpaTest

`@DataJpaTest` uses an in-memory H2 database by default and disables Flyway. To enable Flyway in test slices:

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // use real DB
@TestPropertySource(properties = {
    "spring.flyway.enabled=true",
    "spring.flyway.clean-disabled=false"
})
class UserRepositoryTest {
    // Flyway runs migrations before tests
}
```

For H2 compatibility, either:
- Use ANSI SQL in migrations
- Add H2-specific migrations in `src/test/resources/db/migration/`
- Configure Flyway to pick up test-only location:

```yaml
# application-test.yml
spring:
  flyway:
    locations: classpath:db/migration,classpath:db/test-migration
```

**Recommended pattern for @DataJpaTest with Testcontainers:**

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@Testcontainers
class UserRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("spring.flyway.enabled", () -> "true");
    }
}
```

---

### Multi-Module Projects

Separate migrations per module, merged at the app layer:

```
modules/
  user-module/src/main/resources/db/migration/user/
    V1__create_users.sql
  order-module/src/main/resources/db/migration/order/
    V1__create_orders.sql
app/src/main/resources/application.yml:
  spring.flyway.locations:
    - classpath:db/migration/user
    - classpath:db/migration/order
```

**Pitfall:** Version numbers must be globally unique across all locations. Use module prefixes:

```
db/migration/user/V100__create_users.sql
db/migration/order/V200__create_orders.sql
```

---

### Common Pitfalls

**Checksum failure:**
```
FlywayException: Validate failed: Migration checksum mismatch for migration version 3
```
Cause: Modified a migration file after it was applied.
Fix: Never edit applied migrations. If in dev only, use `flyway:repair` or `flyway:clean` + `flyway:migrate`.

**Out-of-order migrations:**
```
FlywayException: Detected resolved migration not applied to database: Version 2.1
```
Cause: A migration with a lower version number was added after higher versions already ran.
Fix: Enable `out-of-order: true` in dev/CI, or renumber the migration.

**Missing flyway-mysql dependency (MySQL 8+):**
```
ClassNotFoundException: org.flywaydb.database.mysql.MySQLDatabaseType
```
Fix: Add `flyway-mysql` artifact — it's no longer bundled in `flyway-core` as of Flyway 9.

**H2 incompatibility in tests:**
Use PostgreSQL-specific syntax? Run tests against Testcontainers, not H2.

---

## Liquibase

### Dependencies

```xml
<dependency>
    <groupId>org.liquibase</groupId>
    <artifactId>liquibase-core</artifactId>
</dependency>
```

Spring Boot auto-configures Liquibase when `liquibase-core` is on the classpath.

---

### Changelog Format

Liquibase supports XML, YAML, JSON, and SQL. YAML is most readable:

```yaml
# src/main/resources/db/changelog/db.changelog-master.yaml
databaseChangeLog:
  - include:
      file: db/changelog/changes/001-create-users.yaml
  - include:
      file: db/changelog/changes/002-add-email-index.yaml
```

```yaml
# db/changelog/changes/001-create-users.yaml
databaseChangeLog:
  - changeSet:
      id: 001
      author: dev
      changes:
        - createTable:
            tableName: users
            columns:
              - column:
                  name: id
                  type: BIGINT
                  autoIncrement: true
                  constraints:
                    primaryKey: true
                    nullable: false
              - column:
                  name: email
                  type: VARCHAR(255)
                  constraints:
                    nullable: false
                    unique: true
              - column:
                  name: created_at
                  type: TIMESTAMP
                  defaultValueComputed: CURRENT_TIMESTAMP
```

---

### Configuration

```yaml
# application.yml
spring:
  liquibase:
    enabled: true
    change-log: classpath:db/changelog/db.changelog-master.yaml
    contexts: prod                    # run only changeSets tagged with 'prod'
    default-schema: public
    drop-first: false                 # NEVER true in production
    test-rollback-on-update: false
```

---

### Rollback Support

Liquibase supports rollback natively (unlike Flyway Community):

```yaml
- changeSet:
    id: 002
    author: dev
    changes:
      - addColumn:
          tableName: users
          columns:
            - column:
                name: phone
                type: VARCHAR(20)
    rollback:
      - dropColumn:
          tableName: users
          columnName: phone
```

---

### Contexts for Environment-Specific Migrations

```yaml
- changeSet:
    id: 003
    author: dev
    context: dev,test
    changes:
      - insert:
          tableName: users
          columns:
            - column:
                name: email
                value: seed@example.com
```

```yaml
# application-dev.yml
spring:
  liquibase:
    contexts: dev
```

---

### Integration with @DataJpaTest

```java
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
@TestPropertySource(properties = {
    "spring.liquibase.enabled=true",
    "spring.liquibase.contexts=test"
})
@Testcontainers
class OrderRepositoryTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16");

    @DynamicPropertySource
    static void props(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }
}
```

---

### Common Pitfalls

**Duplicate changeSet ID:**
```
LiquibaseException: ChangeSet 001::dev is already in the database
```
Fix: IDs must be unique across the entire changelog. Use a sequential global counter or timestamp prefix.

**Validation failure after changeSet edit:**
```
liquibase.exception.ValidationFailedException: Validation Failed: 1 change sets check sum
```
Fix: Never edit applied changeSets. If unavoidable in dev, use `liquibase:clearChecksums`.

**XML namespace issues:**
Always include the correct XSD reference when using XML format to avoid schema validation errors.

---

## Flyway vs Liquibase Decision Matrix

| Concern | Flyway | Liquibase |
|---|---|---|
| Learning curve | Low (plain SQL) | Medium (DSL + XML/YAML) |
| Rollback support | Teams edition only | Built-in (Community) |
| Database-agnostic DSL | No | Yes |
| Spring Boot integration | Excellent | Excellent |
| Multi-environment contexts | Via profiles | Via contexts |
| Community size | Large | Large |
| Plain SQL migrations | Yes (primary) | Yes (supported) |

**Choose Flyway** when: team prefers plain SQL, rollback is handled by deploy strategy, simplicity matters.

**Choose Liquibase** when: you need rollback scripts, database-agnostic migrations, or per-environment data seeding via contexts.
