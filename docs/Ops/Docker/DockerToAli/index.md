# Docker镜像To阿里云

本地镜像发布到阿里云流程：

![image.png](assets/img202410212008861.png)

## 阿里云

先需要准备阿里云账号，开通**容器镜像服务 ACR**

开通个人实例，在访问凭证中获取账号密码，并创建命名空间

![image-20240620163706557](assets/img202410212241851.png)

## GitHub

创建一个仓库

创建文件夹 `.github/workflows`

在该文件夹下创建yaml文件

示例

```yaml
# .github/workflows/docker-copy-to-ali.yaml
name: Sync Docker Images

on:
  push:
    branches:
      - main

jobs:
  sync-images:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Set up Skopeo
        run: |
          sudo apt-get update
          sudo apt-get install -y skopeo

      - name: Login to Alibaba Cloud Registry
        env:
          # ALIBABA_CLOUD_REGISTRY 示例 registry.cn-beijing.aliyuncs.com
          ALIBABA_CLOUD_REGISTRY: your registry path
          USERNAME: your username
          PASSWORD: your password
        run: |
          echo $PASSWORD | docker login $ALIBABA_CLOUD_REGISTRY -u $USERNAME --password-stdin

      - name: Use Skopeo Tools to Sync Images to Alibaba Cloud
        run: |
          skopeo copy docker://docker.io/library/mysql:8.0.33 docker://registry.cn-beijing.aliyuncs.com/wulan/mysql:8.0.33
          skopeo copy docker://docker.io/canal/canal-server:v1.1.1 docker://registry.cn-beijing.aliyuncs.com/wulan/canal-server:v1.1.1
```

然后点击Actions，运行脚本

![image-20240620163531058](assets/img202410212257347.png)

**注意**：

> skopeo copy docker://docker.io/library/mysql:8.0.33 docker://registry.cn-beijing.aliyuncs.com/wulan/mysql:8.0.33
>
> library 和 wulan为两个镜像仓库的命名空间
>
> docker官方的镜像的命名空间为**library**，非官方的镜像要注意**修改**
>
> 例如：skopeo copy docker://docker.io/**canal**/canal-server:v1.1.1 docker://registry.cn-beijing.aliyuncs.com/wulan/canal-server:v1.1.1

## 本地镜像发布到阿里云

**镜像的生成方法**
方法一：
基于当前容器创建一个新镜像
docker commit [OPTIONS] 容器ID [REPOSITORY[:TAG]]
方法二：
基于DockerFile

**将本地镜像推送到阿里云**
创建仓库镜像 ==> 最终获取管理界面脚本

通过管理界面脚本获取命令，通过命令上传镜像
类似git操作
示例(示例代码中的“[]”在实际中不需要)：

```text
docker login --username=pengnz registry.cn-beijing.aliyuncs.com
docker tag [ImageId] registry.cn-beijing.aliyuncs.com/wulan/myubuntu:[镜像版本号]
docker push registry.cn-beijing.aliyuncs.com/wulan/myubuntu:[镜像版本号]
```

**将阿里云上的镜像下载到本地**
通过命令下载到本地

```text
docker pull registry.cn-beijing.aliyuncs.com/wulan/myubuntu:[镜像版本号]
```
