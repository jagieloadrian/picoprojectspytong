plugins {
    kotlin("jvm") version "2.3.0"
    application
}

group = "org.anjo"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    testImplementation(kotlin("test"))
}

application {
    mainClass.set("org.anjo.MainKt") // <- jeśli Twój plik to Main.kt
}

tasks.jar {
    manifest {
        attributes["Main-Class"] = "org.anjo.MainKt"
    }
    from(configurations.runtimeClasspath.get().map { if (it.isDirectory) it else zipTree(it) })
}

kotlin {
    jvmToolchain(17)
}

tasks.test {
    useJUnitPlatform()
}