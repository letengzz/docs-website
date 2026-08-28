# 安装与集群搭建

学习环境用 **minikube / kind / k3s**，生产环境用 **kubeadm** 或云厂商托管（EKS、ACK、TKE 等）。这一篇给出常用安装方式和一套 kubeadm 集群搭建流程。

## 安装 kubectl

```shell
# Linux (amd64)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl

# Windows
choco install kubernetes-cli
```

验证：

```shell
kubectl version --client
```

## 本地学习环境：minikube

```shell
# Linux / macOS
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 启动单节点集群
minikube start --driver=docker
kubectl get nodes
```

替代方案：

- **kind**：用 Docker 跑多节点集群，适合 CI。
- **k3s**：轻量发行版，适合边缘与资源受限环境。

## 生产环境：kubeadm 搭建（以 Ubuntu 为例）

### 1. 环境准备（所有节点）

```shell
sudo apt update
sudo apt install -y containerd
sudo systemctl enable --now containerd

# 关闭 swap（kubelet 要求）
sudo swapoff -a
sudo sed -i '/ swap / s/^/#/' /etc/fstab

# 加载内核模块
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
```

### 2. 安装 kubeadm / kubelet / kubectl

```shell
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.37/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.37/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

### 3. 初始化控制平面

```shell
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# 配置 kubectl
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

输出末尾会给出 worker 节点加入命令（`kubeadm join ...`），请保存。

### 4. 安装网络插件（CNI）

```shell
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
# 或 Calico：kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/master/manifests/calico.yaml
```

### 5. 工作节点加入

在 worker 节点执行上一步保存的 join 命令，然后回到控制平面验证：

```shell
kubectl get nodes
kubectl get pods -n kube-system
```

## 版本匹配原则

`kubectl`、`kubeadm` 与集群版本差异不要超过 1 个次要版本；升级集群按「控制平面 → 节点」顺序，一次跳一个次要版本。

## 易错点

::: danger 常见错误
1. 没关 swap：kubelet 启动失败或节点 NotReady。
2. containerd 的 cgroup 驱动与 kubelet 不一致：Pod 反复 CrashLoopBackOff。
3. 忘记安装 CNI：节点 Ready 但 Pod 一直 ContainerCreating。
4. `kubeadm join` 令牌过期：默认 24 小时，用 `kubeadm token create --print-join-command` 重新生成。
5. 控制平面默认不允许调度业务 Pod：单节点测试要执行 `kubectl taint nodes --all node-role.kubernetes.io/control-plane-`。
6. 直接 apt upgrade k8s 组件：先解除 hold 再按官方升级流程操作。
:::

## 验证方式

1. `kubectl get nodes`：全部 Ready。
2. `kubectl get pods -A`：核心组件 Running。
3. 部署一个测试应用并 `kubectl expose`，确认可访问。

## 参考资料

- kubeadm 安装指南：https://kubernetes.io/zh-cn/docs/setup/production-environment/tools/kubeadm/
- minikube：https://minikube.sigs.k8s.io/docs/
- kind：https://kind.sigs.k8s.io/
