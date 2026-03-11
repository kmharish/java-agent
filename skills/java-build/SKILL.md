---
name: java-build
description: Build, test, and lint Java projects with Maven or Gradle
tools: [bash, read_file, write_file, edit_file]
---

# Java Build Skill

## Detecting the Build System

Before running any build command, detect the build system:
1. If `pom.xml` exists → **Maven** project
2. If `build.gradle` or `build.gradle.kts` exists → **Gradle** project
3. If both exist, prefer the one with a wrapper script (`mvnw` or `gradlew`)

## Maven Commands

```bash
# Always prefer the wrapper when available
./mvnw clean compile          # Compile
./mvnw clean test             # Run tests
./mvnw clean verify           # Full verification (compile + test + integration tests)
./mvnw clean package -DskipTests  # Build JAR/WAR without tests
./mvnw dependency:tree        # Show dependency tree
./mvnw versions:display-dependency-updates  # Check for outdated deps
```

## Gradle Commands

```bash
./gradlew clean build         # Full build
./gradlew test                # Run tests
./gradlew check               # Run all checks (tests + static analysis)
./gradlew dependencies        # Show dependency tree
./gradlew bootRun             # Run Spring Boot app
```

## After Every Code Change

1. Run the build: `./mvnw clean compile` or `./gradlew clean build`
2. Run tests: `./mvnw test` or `./gradlew test`
3. If tests fail, read the error output carefully and fix
4. Check for compiler warnings — treat them as errors

## Common Issues

- **Dependency resolution failures**: Check if the artifact exists in Maven Central. Run `./mvnw dependency:resolve` to diagnose.
- **Java version mismatch**: Check `java -version` and the `<java.version>` property in pom.xml or `sourceCompatibility` in build.gradle.
- **Test failures**: Read the full stack trace. Check `target/surefire-reports/` (Maven) or `build/reports/tests/` (Gradle) for detailed reports.
- **Spring context failures**: Usually a missing bean or circular dependency. Check `@Component`, `@Service`, `@Repository` annotations.

## Multi-module Projects

For multi-module Maven projects:
```bash
./mvnw clean test -pl module-name        # Test a specific module
./mvnw clean test -pl module-name -am    # Test module + its dependencies
```

For Gradle:
```bash
./gradlew :module-name:test              # Test a specific module
```
