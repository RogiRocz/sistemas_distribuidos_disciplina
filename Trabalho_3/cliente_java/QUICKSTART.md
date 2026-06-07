# 🚀 INÍCIO RÁPIDO - Cliente Java

## ⚡ Comando Único (Linux/Mac)

```bash
cd cliente_java

# 1. Crie os diretórios
mkdir -p bin lib

# 2. Baixe o GSON (uma vez apenas)
wget https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar -O lib/gson-2.10.1.jar

# 3. Compile
javac -cp "lib/*" -d bin src/*.java

# 4. Execute
java -cp "bin:lib/*" Main
```

---

## 🪟 No Windows (PowerShell)

```powershell
cd cliente_java

# 1. Crie os diretórios
New-Item -ItemType Directory -Force -Path bin, lib

# 2. Baixe GSON
Invoke-WebRequest -Uri "https://repo1.maven.org/maven2/com/google/code/gson/gson/2.10.1/gson-2.10.1.jar" -OutFile "lib/gson-2.10.1.jar"

# 3. Compile
javac -cp "lib/*" -d bin src/*.java

# 4. Execute
java -cp "bin;lib/*" Main
```

---

## 📱 Ou use Maven (Alternativa)

1. Crie um `pom.xml` na pasta `cliente_java`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.sebo</groupId>
    <artifactId>cliente-java</artifactId>
    <version>1.0</version>

    <properties>
        <maven.compiler.source>11</maven.compiler.source>
        <maven.compiler.target>11</maven.compiler.target>
    </properties>

    <dependencies>
        <dependency>
            <groupId>com.google.code.gson</groupId>
            <artifactId>gson</artifactId>
            <version>2.10.1</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.11.0</version>
                <configuration>
                    <source>11</source>
                    <target>11</target>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-assembly-plugin</artifactId>
                <version>3.6.0</version>
                <configuration>
                    <archive>
                        <manifest>
                            <mainClass>Main</mainClass>
                        </manifest>
                    </archive>
                    <descriptorRefs>
                        <descriptorRef>jar-with-dependencies</descriptorRef>
                    </descriptorRefs>
                </configuration>
                <executions>
                    <execution>
                        <phase>package</phase>
                        <goals>
                            <goal>single</goal>
                        </goals>
                    </execution>
                </executions>
            </plugin>
        </plugins>
    </build>
</project>
```

2. Compile com Maven:
```bash
mvn clean compile exec:java -Dexec.mainClass="Main"
```

---

## 🎯 Certificados de que funciona:

✅ **Java 11+** necessário  
✅ **GSON 2.10.1** como única dependência  
✅ Sem frameworks pesados  
✅ Código limpo e profissional  

---

## 🔗 Links Úteis

- [Instalar Java](https://www.oracle.com/java/technologies/javase-downloads.html)
- [GSON no Maven](https://mvnrepository.com/artifact/com.google.code.gson/gson)
- [Documentação GSON](https://github.com/google/gson)

---

**Dúvidas? Revise o README.md ou veja o código em `src/`!**
