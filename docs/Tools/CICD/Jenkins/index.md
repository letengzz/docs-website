# Jenkins 流水线

Jenkins 是历史最悠久、插件生态最庞大的 CI/CD 服务器：它本身只是一个调度平台，通过插件连接 Git、构建工具、K8s、制品库等一切系统。Jenkins 适合已有 Java/企业基础设施、需要高度定制流程的团队。截至 2026 年 8 月，最新 LTS 为 **2.568.x**（支持 JDK 17/21/25）。

![流水线阶段](../assets/pipeline-stages.svg)

## 安装与初始化

### Docker 方式

```shell [docker-compose.yml]
services:
  jenkins:
    image: jenkins/jenkins:lts-jdk21
    container_name: jenkins
    ports:
      - "8080:8080"
      - "50000:50000"   # agent 连接端口
    volumes:
      - jenkins-home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
volumes:
  jenkins-home:
```

```shell
docker compose up -d
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

浏览器访问 http://localhost:8080，粘贴初始密码，安装推荐插件并创建管理员账号。

## 两种任务形态

| 形态 | 说明 | 适用 |
| --- | --- | --- |
| Freestyle Job | 图形化配置：源码、构建步骤、触发器 | 简单任务、新手 |
| Pipeline | **流水线即代码**（Jenkinsfile） | 复杂流程、团队协作、评审 |

::: tip 推荐 Pipeline
Jenkinsfile 进代码库，配置随代码走：可评审、可回溯、可复用，这是 Jenkins 的最佳实践。
:::

## 声明式 Pipeline 基础

```groovy [Jenkinsfile]
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                sh 'mvn -B clean package'
            }
        }
        stage('Test') {
            steps {
                sh 'mvn -B test'
            }
            post {
                always {
                    junit 'target/surefire-reports/*.xml'
                    archiveArtifacts artifacts: 'target/*.jar'
                }
            }
        }
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh './deploy.sh'
            }
        }
    }

    post {
        success { echo '构建成功' }
        failure { echo '构建失败' }
    }
}
```

## Pipeline 核心语法

### agent：在哪里执行

```groovy
pipeline {
    agent any                     // 任意可用节点
    // agent { label 'docker' }   // 指定标签节点
    // agent { docker 'maven:3.9' }  // 在容器里执行
}
```

### stages / steps：做什么

```groovy
stage('并行测试') {
    parallel {
        stage('单元测试') {
            steps { sh 'mvn test' }
        }
        stage('E2E 测试') {
            steps { sh 'npm run test:e2e' }
        }
    }
}
```

### 参数与凭据

```groovy
pipeline {
    parameters {
        choice(name: 'ENV', choices: ['dev', 'staging', 'prod'], description: '目标环境')
        string(name: 'VERSION', defaultValue: '1.0.0', description: '版本号')
    }
    environment {
        REGISTRY = 'registry.example.com'
    }
    stages {
        stage('Deploy') {
            steps {
                withCredentials([string(credentialsId: 'server-token', variable: 'TOKEN')]) {
                    sh "curl -H \"Authorization: Bearer $TOKEN\" ..."
                }
            }
        }
    }
}
```

## 构建触发器

### 轮询与 Webhook

```groovy
triggers {
    // 轮询（不推荐，浪费资源）
    pollSCM('H/5 * * * *')
    // GitHub Webhook（推荐）
    githubPush()
}
```

### 定时构建

```groovy
triggers {
    cron('0 2 * * *')   // 每天 2 点（服务器时区）
}
```

## 多分支流水线

**Multibranch Pipeline** 自动发现仓库分支，每个分支一个流水线：

1. 新建 Item → 选择 **Multibranch Pipeline**。
2. 配置 Git 仓库地址。
3. 指定 Build Configuration 为 `Jenkinsfile`。
4. 保存后 Jenkins 自动扫描分支，每个含 Jenkinsfile 的分支生成独立任务。

配合 **Branch Source 插件** 还可以为每个 PR 自动建流水线。

## 共享库（Shared Library）

把公共逻辑抽到共享库，流水线只写业务步骤：

```groovy
// 仓库：my-org/jenkins-library
// vars/deployToK8s.groovy
def call(String env) {
    echo "deploying to ${env}"
    sh "kubectl apply -f k8s/${env}/"
}
```

```groovy
pipeline {
    stages {
        stage('Deploy') {
            steps {
                deployToK8s('staging')   // 调用共享库方法
            }
        }
    }
}
```

## 插件生态速览

| 插件 | 用途 |
| --- | --- |
| Git / GitHub | 源码拉取、Webhook |
| Pipeline / Blue Ocean | 流水线与可视化界面 |
| Docker Pipeline | 构建、推送镜像 |
| Kubernetes | 动态创建 agent Pod |
| Credentials Binding | 凭据管理 |
| JUnit / HTML Publisher | 测试报告展示 |
| SonarQube Scanner | 代码扫描 |
| Slack / DingTalk | 通知 |
| Ansible / SSH | 部署 |

## 易错点与最佳实践

::: danger 常见错误
1. **用 Freestyle 写复杂流程**：点击式配置无法评审、无法版本化，多环境就失控。
2. **Jenkinsfile 不检查**：语法错误只有运行时才发现，先 `jenkins validate` 或本地 Groovy 校验。
3. **agent 全部 `any`**：任务可能跑到不同环境，依赖不一致；用标签或固定节点。
4. **密钥写 Jenkinsfile**：用 Credentials 插件 + `withCredentials`。
5. **JENKINS_HOME 不持久化**：容器重建全部配置丢失；挂载卷是必须的。
6. **不设并发限制**：同一任务并发执行互相覆盖工作区；用 `disableConcurrentBuilds()` 或资源锁。
:::

::: tip 最佳实践
1. 单次构建产物只保留最近 N 个（`buildDiscarder`），避免磁盘爆炸。
2. 使用 Docker/K8s agent 保证环境一致，agent 即镜像。
3. 流水线收尾统一 `post { always {} }` 处理归档、通知。
4. 控制台日志用 AnsiColor/Timestamper 插件增强可读性。
5. 高可用：Jenkins 主节点 + 多个 agent；备份 `JENKINS_HOME` 配置与凭据。
:::

## 验证方式

1. 新建一个 Pipeline 任务，指向含 Jenkinsfile 的仓库，运行后确认各 stage 全部通过。
2. 故意让测试失败，确认构建标红、`post.failure` 触发通知。
3. 配置 Multibranch Pipeline，推送新分支后确认自动发现并构建。
4. 用 `buildDiscarder` 设置保留 10 次构建，多次构建后确认旧记录被清理。

## 参考资料

- Jenkins 官方文档：https://www.jenkins.io/doc/
- Pipeline 语法参考：https://www.jenkins.io/doc/book/pipeline/syntax/
- Jenkinsfile 示例：https://www.jenkins.io/doc/pipeline/examples/
- Jenkins LTS 版本信息：https://endoflife.date/jenkins
- Blue Ocean 文档：https://www.jenkins.io/projects/blueocean/
