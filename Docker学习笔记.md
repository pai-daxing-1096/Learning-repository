## Docker学习笔记

---

---

### 一.Docker的发展历程

#### 1.Docker的早期架构

首发架构主要依赖 **LXC** 作为底层容器运行时，上层由 **Docker Daemon** 提供镜像管理、API 等应用功能。

**Docker的首发架构由两大核心组件构成**：

- **LXC(Linux Container)：**Linux 内核的容器能力封装，负责容器的创建与运行。
- **Docker Daemon：**提供镜像构建、容器生命周期管理、远程 API 等服务。

**存在的问题：**

- **强依赖 LXC**：LXC 本身的版本差异、功能限制会“卡住” Docker 的发展。
- **跨平台能力弱**：LXC 仅支持 Linux，无法直接运行在 FreeBSD、macOS、Windows 等系统上。
- **单体架构臃肿**：所有功能集中在一个 Daemon 进程中，更新困难，性能存在瓶颈。
- **中心化风险**：Docker Daemon 一旦崩溃，所有管理的容器都会受到影响。

#### 2.Docker0.9版本架构

Docker 团队开发了 **libcontainer** 替代 LXC，实现对 Linux 内核系统调用（namespaces、cgroups 等）的直接调用，不再依赖外部工具。

**变化：**

- 移除对 LXC 的依赖，彻底解决“卡脖子”问题。
- 为后续跨平台（如 Windows 容器）奠定了基础。
- 架构仍保持“Docker Daemon 大单体”模式，但内部实现更自主。

#### 3.Docker1.11版本架构

随着 OCI（Open Container Initiative）规范的成熟，Docker 将自己开发的 **runC** 捐赠给 OCI 作为参考实现，并将容器运行时从 Docker Daemon 中剥离。

- **OCI 规范**：定义了镜像格式和运行时标准，使不同容器引擎可以兼容。
- **containerd**：Docker 将运行时管理抽离为 containerd 进程，负责容器的生命周期（启动、停止、资源监控）。
- **runC**：containerd 调用的底层运行时，实际执行容器创建。

**新架构：**

```
Docker Client → Docker Daemon → containerd → runC → 容器进程
```

- Docker Daemon 不再直接创建容器，而是通过 gRPC 调用 containerd。
- 即使 Docker Daemon 崩溃，运行中的容器也不会受影响（containerd 独立运行）。

#### 4. 后续演进

- **Moby 项目**：Docker 将开源部分重构为 Moby 工程，方便社区定制。
- **dockerd 功能持续瘦身**：将网络、存储、镜像分发等模块也逐步可插拔化。
- **与 Kubernetes 集成**：Docker 作为容器运行时之一，通过 CRI（Container Runtime Interface）被 Kubernetes 调用（后推荐使用 containerd 直接集成）。

#### 5.要点总结

| 版本/时期    | 关键变化                         | 解决的问题                    |
| :----------- | :------------------------------- | :---------------------------- |
| 早期 (~0.8)  | 依赖 LXC                         | 功能受限，跨平台差            |
| 0.9 (2014)   | 引入 libcontainer                | 解除对 LXC 的依赖             |
| 1.11 (2016)  | 拆分 containerd + runC，拥抱 OCI | Daemon 崩溃不影响容器，标准化 |
| 1.13+ / Moby | 模块化架构                       | 可插拔，性能优化              |

### 二.Docker引擎

##### 1.Docker引擎架构

Docker 引擎是用来运行和管理容器的核心软件，其现代架构由四部分主要组件构成：

- Docker Client

- Dockerd

- Containerd

- lhunc

##### (1)Docker Client

Docker客户端，Docker 引擎提供的凵工具，用于用户向 Docker 提交命令请求。

##### (2)Dockerd

Dockerd，即Docker Daemon在现代Dockerd 中的主要包含的功能有：镜像构建、镜像管理、REST API、核心网络及编排等。其通过gRPC与Containerd进行通信。

**核心职责**：负责与用户交互、管理镜像网络，接收API请求后调用Containerd执行任务

##### (3)Containerd

Containerd，即Container Daemon，该项目的主要功能是管理容器的生命周期。不过，其本身并不会去创建容器，而是调用Runc来完成容器的创建。Docker公司后来将Containerd项目捐献给了CNCF。

**核心职责**：专注于管理容器的完整生命周期（增删改查），是Docker Daemon与下层执行器之间的桥梁

##### (4)Runc

Runc，Run Container，是OCI容器运行时规范的实现，Runc项目的目标之一就是与OCI规范保持一致。所以，Runc 所在层也称为OCI层。这使得Docker Daemon中不用再包含任何容器运行时的代码了，简化了Docker Daemon。

Runc只有一个作用，即创建容器，其本质是一个独立的容器运行时CLI工具。其在fork出一个容器子进程后会启动该容器进程。在容器进程启动完毕后，Runc会自动退出。

**核心职责**：按照OCI标准创建容器环境并启动进程，启动完成后立即退出，不占用系统资源

##### (5)shim

Shim是实现“Daemonless Container”不可或缺的工具，使容器与Docker Daemon解耦，使得Docker Daemon的维护与升级不会影响到运行中的容器。

每次创建容器时，Containerd会先fork出Shim进程，再由Shim进程fork出Runc进程。当Runc自动退出之前，会先将新容器进程的父进程指定为相应的Shim进程。除了作为容器的父进程外，Shim进程还具有两个重要功能：

- 保持所有STDIN与STDOUT流的开启状态，从而使得当Docker Daemon重启时，容器不会因为Pipe的关闭而终止。

- 将容器的退出状态反馈给Docker Daemon。

**核心职责**：作为容器进程的直接“管家”，负责监控、收集状态上报，并保持stdin/stdout打开

![image-20260402185753807](C:/Users/24846/AppData/Roaming/Typora/typora-user-images/image-20260402185753807.png)

---

### 三.Docker安装与卸载

##### 1.安装流程

```shell
#添加Docker软件包源
sudo wget -O /etc/yum.repos.d/docker-ce.repo http://mirrors.cloud.aliyuncs.com/docker-ce/linux/centos/docker-ce.repo
sudo sed -i 's|https://mirrors.aliyun.com|http://mirrors.cloud.aliyuncs.com|g' /etc/yum.repos.d/docker-ce.repo
#Alibaba Cloud Linux3专用的dnf源兼容插件
sudo dnf -y install dnf-plugin-releasever-adapter --repo alinux3-plus
#安装Docker社区版本，容器运行时containerd.io，以及Docker构建和Compose插件
sudo dnf -y install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
#启动Docker
sudo systemctl start docker
#设置Docker守护进程在系统启动时自动启动
sudo systemctl enable docker
```

##### 2.版本检查

```shell
docker version
```

##### 3.配置镜像加速

```shell
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": ["https://iyp5qae4.mirror.aliyuncs.com"]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

##### 4.卸载

```
yum remove docker-ce docker-ce-cli containerd.io docker-compose-plugin docker-buildx-plugin
rm -rf /var/lib/docker
rm -rf /var/lib/containerd
rm -rf /etc/docker
rm -rf /etc/systemd/system/docker.service.d
rm -f /etc/systemd/system/docker.servic
```

