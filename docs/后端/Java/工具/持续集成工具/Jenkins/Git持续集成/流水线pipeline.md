# 流水线 pipeline

流水线既能作为任务的本身，也能作为Jenkinsfile

使用流水线可以让我们的任务从ui手动操作，转换为代码化，像docker的dockerfile一样，从shell命令到配置文件，更适合大型项目，可以让团队其他开发者同时参与进来，同时也可以编辑开发Jenkinswebui不能完成的更复杂的构建逻辑，作为开发者可读性也更好。

## 流水线方式

#### 声明式流水线

好处：

- 更像是在Jenkins web ui中的操作
- 可读性比较高
- 可以使用blue ocean自动生成
- 支持语法检查

坏处：

- 代码逻辑能力比脚本式弱，不能完成特别复杂的任务	

#### 脚本式流水线

好处：

- 更少的代码和弱规范要求
- 更灵活的自定义代码操作
- 不受约束，可以构建特别复杂的工作流和流水线

坏处：

- 读写对编程要求比较高
- 比声明式流水线代码更复杂

## 创建流水线任务

![image-20240404202405714](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042024286.png)

### 完整语法

5个必备的组成部分：

- pipeline：整条流水线
- agent：指定执行器
- stages：所有阶段
- stage：某一阶段，可有多个
- steps：阶段内的每一步，可执行命令

### 测试脚本

#### 基础框架

```groovy
pipeline {
    agent any

    stages {
        stage('拉取代码') {
            steps {
                echo '拉取代码完成'
               
            }

        }
        stage('执行构建') {
            steps {
                echo '执行构建完成'

            }

        }
    }
    
    post {
        
        always {
            
            echo "完成"
            
        }
        
        failure {
            
            echo "失败"
        }
    }
}
```

#### 阶段视图 Stage View

执行上述操作，会展示出每个阶段的视图：

![image-20240404204834974](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042048698.png)

查看日志：

![image-20240404204858022](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042048800.png)

#### post

流水线完成后可执行的任务

- always 无论流水线或者阶段的完成状态。
- changed 只有当流水线或者阶段完成状态与之前不同时。
- failure 只有当流水线或者阶段状态为"failure"运行。
- success 只有当流水线或者阶段状态为"success"运行。
- unstable 只有当流水线或者阶段状态为"unstable"运行。例如：测试失败。
- aborted 只有当流水线或者阶段状态为"aborted "运行。例如：手动取消。

#### agent

可以指定执行节点

label 指定运行job的节点标签

any 不指定，由Jenkins分配

```
pipeline {
    agent {
        node {
            label "jenkins-02"
        }
        
    }

    stages {
        stage('拉取代码') {
            steps {
          
                sh """
                    sleep 10
                            
                   """

                echo '拉取代码完成'
               
            }

        }
        stage('执行构建') {
            steps {
                echo '执行构建完成'


            }

        }
    }
    
    post {
        
        always {
            
            echo "完成"
            
        }
        
        failure {
            
            echo "失败"
        }
    }
}

```

## 查看日志

查看执行日志：

![image-20240404205010545](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042050152.png)

## 执行指定阶段

![image-20240404205142092](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042051835.png)

## 可视化界面

### blue ocean

全新的流水线控制ui，可重复执行某阶段代码

插件中心搜索blue ocean安装即可

![image-20240404205328574](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042053159.png)

打开Blue Ocean：

![image-20240404205838588](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042058128.png)

## pipeline中执行自动化构建

**使用片段生成器**：

![image-20240404211907746](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042119600.png)

**创建Git拉取**：

![image-20240404212559899](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042126324.png)

![image-20240404212649006](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404042126622.png)

**创建Maven拉取**：需要提前将Maven声明(后面是设置中配置的Maven的名称)：

```groovy
tools {
	maven "maven" 
}
```

**调用sh**：

```
sh "mvn --version"
sh """ 
    cd demo-1
    mvn clean package
"""
```

**删除服务器镜像**：

```groovy
sshPublisher(publishers: [sshPublisherDesc(configName: 'DockerServer', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '''rm -rf *
docker stop mdemo
docker rm mdemo
docker rmi mydemo''', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '', remoteDirectorySDF: false, removePrefix: '', sourceFiles: '')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
```

**发送jar包到测试服务器**：

```groovy
sshPublisher(publishers: [sshPublisherDesc(configName: 'DockerServer', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '/', remoteDirectorySDF: false, removePrefix: 'demo/target', sourceFiles: '**/demo*.jar')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false), sshPublisherDesc(configName: 'DockerServer', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '''docker build -t mydemo .
docker run -d --name mdemo -p 9999:9999 mydemo''', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '/', remoteDirectorySDF: false, removePrefix: '', sourceFiles: '')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
```

****

自动打包Docker镜像：

```
pipeline {
    agent any

    tools {
        
        maven "maven"
        
    }
    stages {
        stage("拉取代码") {
            steps {
                git branch: 'main', credentialsId: 'gitlab', url: 'http://192.168.84.137/root/git-repo.git'
                echo '拉取成功'
            }
        }

        stage("执行构建") {
            steps {
                
            //    sh "mvn --version"
                sh """ 
                cd demo
                
                mvn clean package
                """
                
                echo '构建完成'
            }

        }
        
        
        stage("clean test server"){
            
            steps{
	sshPublisher(publishers: [sshPublisherDesc(configName: 'DockerServer', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '''rm -rf *
docker stop mdemo
docker rm mdemo
docker rmi mydemo''', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '', remoteDirectorySDF: false, removePrefix: '', sourceFiles: '')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
            }
        }
        
        
        
        
        
        stage("发送jar包到测试服务器") {
            steps {
                sshPublisher(publishers: [sshPublisherDesc(configName: 'DockerServer', transfers: [sshTransfer(cleanRemote: false, excludes: '', execCommand: '', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '/', remoteDirectorySDF: false, removePrefix: 'demo/target', sourceFiles: '**/demo*.jar'), sshTransfer(cleanRemote: false, excludes: '', execCommand: '''docker build -t mydemo .
docker run -d --name mdemo -p 9999:9999 mydemo''', execTimeout: 120000, flatten: false, makeEmptyDirs: false, noDefaultExcludes: false, patternSeparator: '[, ]+', remoteDirectory: '/', remoteDirectorySDF: false, removePrefix: '', sourceFiles: 'Dockerfile')], usePromotionTimestamp: false, useWorkspaceInPromotion: false, verbose: false)])
                echo 'jar send over!'
            }

        }

    }
}

```

## 多分支流水线

在Git上创建多个分支做不同的构建。

创建多分支流水线：

![image-20240405111706516](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153242.png)

![image-20240405111915371](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153406.png)

![image-20240405112704726](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153517.png)

配置用户：

![image-20240405112726077](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153671.png)

配置Jenkinsfile存放目录：

![image-20240405112756552](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153843.png)

![image-20240405113305593](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153057.png)

![image-20240405114415515](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153953.png)

![image-20240405114433230](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153152.png)

立即扫描多分支流水线：

![image-20240405114531740](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051153726.png) 	

此时打开：

![image-20240405114644339](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202404051152239.png)
