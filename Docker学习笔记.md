##  Docker学习笔记

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

---

---

### 二.Docker引擎

##### 1.Docker引擎架构

Docker 引擎是用来运行和管理容器的核心软件，其现代架构由四部分主要组件构成：

- Docker Client

- Dockerd

- Containerd

- lhunc

###### (1)Docker Client

Docker客户端，Docker 引擎提供的工具，用于用户向 Docker 提交命令请求。

###### (2)Dockerd

Dockerd，即Docker Daemon在现代Dockerd 中的主要包含的功能有：镜像构建、镜像管理、REST API、核心网络及编排等。其通过gRPC与Containerd进行通信。

**核心职责**：负责与用户交互、管理镜像网络，接收API请求后调用Containerd执行任务

###### (3)Containerd

Containerd，即Container Daemon，该项目的主要功能是管理容器的生命周期。不过，其本身并不会去创建容器，而是调用Runc来完成容器的创建。Docker公司后来将Containerd项目捐献给了CNCF。

**核心职责**：专注于管理容器的完整生命周期（增删改查），是Docker Daemon与下层执行器之间的桥梁

###### (4)Runc

Runc，Run Container，是OCI容器运行时规范的实现，Runc项目的目标之一就是与OCI规范保持一致。所以，Runc 所在层也称为OCI层。这使得Docker Daemon中不用再包含任何容器运行时的代码了，简化了Docker Daemon。

Runc只有一个作用，即创建容器，其本质是一个独立的容器运行时CLI工具。其在fork出一个容器子进程后会启动该容器进程。在容器进程启动完毕后，Runc会自动退出。

**核心职责**：按照OCI标准创建容器环境并启动进程，启动完成后立即退出，不占用系统资源

###### (5)shim

Shim是实现“Daemonless Container”不可或缺的工具，使容器与Docker Daemon解耦，使得Docker Daemon的维护与升级不会影响到运行中的容器。

每次创建容器时，Containerd会先fork出Shim进程，再由Shim进程fork出Runc进程。当Runc自动退出之前，会先将新容器进程的父进程指定为相应的Shim进程。除了作为容器的父进程外，Shim进程还具有两个重要功能：

- 保持所有STDIN与STDOUT流的开启状态，从而使得当Docker Daemon重启时，容器不会因为Pipe的关闭而终止。

- 将容器的退出状态反馈给Docker Daemon。

**核心职责**：作为容器进程的直接“管家”，负责监控、收集状态上报，并保持stdin/stdout打开

![image-20260402185753807](C:/Users/24846/AppData/Roaming/Typora/typora-user-images/image-20260402185753807.png)

---

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

---

---

### 四.docker命令

#### 1.docker pull命令

拉取一个镜像、仓库

语法：

`docker pull [OPTIONS] NAME[:TAG|@DIGEST]`

- `OPTIONS`   参数
- `NAME`   镜像名称
- `:TAG`   版本号
- `@DIGEST`   哈希值

| OPTIONS                   | 作用                       | 示例                                                         | 结果                                                         |
| ------------------------- | -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 无                        | 无                         | `docker pull <镜像名称>:<版本号>`                            | 拉取指定镜像的指定版本                                       |
| 无                        | 无                         | `docker pull centos@sha256:80b1813d991d...(64位)`            | 拉取centos镜像哈希值为80b1813d991d(64位)的版本               |
| `-a`或`--all-tags`        | 下载所有镜像               | `docker pull -a <镜像名称>`                                  | 拉取指定镜像的所有版本                                       |
| `--disable-content-trust` | 跳过镜像验证（默认不跳过） | `docker pull --disable-content-trust <仓库名/镜像名称>:<版本号>` | 拉取非官方镜像的指定版本，并且跳过验证                       |
| `--platform string`       | 拉去其它架构的版本         | `docker pull --platform linux/arm64 <镜像名称>:<版本号>`     | 拉取官方指定镜像的arm64架构的指定版本                        |
| `-q`                      | 不显示过程                 | `docker pull -q <镜像名称>:<版本号>`                         | 拉取指定镜像的指定版本，但是是静默拉取，不显示进度条等过程信息 |

---

#### 2.docker images命令

显示本地镜像

语法：

`docker images [OPTIONS] [REPOSITORY[:TAG]]`

- `[OPTIONS]`   参数
- `[REPOSITORY]`    仓库名/镜像名
- `[:TAG]`   版本号

| OPTIONS       | 作用                                                         | 示例                                              | 结果                                                         |
| ------------- | ------------------------------------------------------------ | ------------------------------------------------- | ------------------------------------------------------------ |
| `-a`或`--all` | 显示所有镜像（默认不显示中间层镜[^1]像）                     | `docker images -a`                                | 显示本地的所有镜像                                           |
| `--digests`   | 显示DIGEST（远程仓库中镜像+版本对应的哈希值）                | `docker images --digests`                         | 显示镜像在镜像清单中所对应的64位哈希值                       |
| `-f`          | 显示指定规则所包括的镜像                                     | `docker images -f since=<镜像名称>:<版本号>`      | 显示指定镜像前面的所有镜像                                   |
| `--format`    | 格式化输出                                                   | `docker images --format {{.Repository}}:{{.Tag}}` | 只显示出镜像的名称和版本号（`{{.列总称}}`，`:`为分隔符）     |
| `--no-trunc`  | 显示出IMAGE ID（本地中镜像+版本对应的哈希值）的64位而非前12位 | `docker images --no-trunc`                        | 显示出本地镜像的64位哈希值                                   |
| `-q`          | 只显示IMAGE ID的前12位哈希值                                 | `docker images -q`                                | 只显示出本地镜像的前12位哈希值，不显示REPOSITORY、TAG、CREATED和SIZE（可以配合`--no-trunc`显示出64位） |

| 规则      | 作用                                 | 示例                                          | 结果                                                         |
| --------- | ------------------------------------ | --------------------------------------------- | ------------------------------------------------------------ |
| since     | 列出所有创建时间晚于 `centos` 的镜像 | `docker images -f since=<镜像名称>:<版本号>`  | 列出所有创建时间晚于指定的镜像的镜像                         |
| before    | 列出所有创建时间早于 `centos` 的镜像 | `docker images -f before=<镜像名称>:<版本号>` | 列出所有创建时间早于指定的镜像的镜像                         |
| reference | 按镜像名称过滤（可以使用通配符）     | `docker images -f reference=c*`               | 列出所有以c开头的镜像，可以重复使用：`docker images -f reference=ubuntu:* -f since=ubuntu:20.04`（注意：`since` / `before` 不支持通配符，必须指定具体镜像） |
| dangling  | 显示出所有悬空镜像                   | `docker images -f dangling=true`              | 显示出所有<none>:<none>` 的镜像                              |

> [!NOTE]
>
> `since` / `before` 的判断依据是镜像的 **创建时间（Created）**，而非拉取时间。参数可以使用镜像名（含 tag）或 IMAGE ID

> Digest 是**内容**的哈希，即使标签被覆盖或移动到其他仓库，Digest 不变

> [!IMPORTANT]
>
> 当没有指定`:TAG`即版本时，会默认指定latest即最新版本，如果需要查询所有版本应当使用`docker images -f reference=<镜像名>:*`

---

#### 3.docker search命令

从docker hub上查看指定名称的镜像

语法：

`docker search [OPTIONS] TERM`

- `[OPTIONS]`   参数
- `TERM`   用于模糊匹配镜像仓库名称，通常就是你想找的那个镜像的名字或名字中的关键词

示例：

```dockerfile
[root@AliYunLinux ~]# docker search zookeeper
NAME                    DESCRIPTION                                      STARS    OFFICIAL    AUTOMATED
zookeeper               Apache ZooKeeper is an open-source server wh...  1299     [OK]
wurstmeister/zookeeper                                                   175                  [OK]
jplock/zookeeper        Builds a docker image for Zookeeper version ...  165                  [OK]
bitnami/zookeeper       ZooKeeper is a centarlized service for distr...  86                   [OK]
......
```

- `NAME`   仓库名/镜像名
- `DESCRIPTION`   简介
- `STARS`   收藏数量
- `OFFICIAL`   是否为官方验证的镜像
- `AUTOMATED`   是否为自动化镜像

| OPTIONS      | 作用                       | 示例                                   | 结果                                  |
| ------------ | -------------------------- | -------------------------------------- | ------------------------------------- |
| -f           | 按指定条件过滤镜像         | `docker search -f stars=100 zookeeper` | 显示出所有收藏数量大于等于100的镜像   |
| `--limit`    | 最多显示多少行（默认25条） | `docker search --limit=5 zookeeper`    | 只显示出前5条镜像                     |
| `--no-trunc` | 显示出全部的简介内容       | `docker search --no-trunc zookeeper`   | 显示出简介的全部内容而非使用`...`省略 |

| 过滤条件（主要用于-f参数） | 作用                        | 示例                                       |
| :------------------------- | :-------------------------- | :----------------------------------------- |
| `stars=N`                  | 只显示收藏数大于等于N的镜像 | `docker search -f stars=100 nginx`         |
| `is-official=true`         | 只显示官方认证的镜像        | `docker search -f is-official=true nginx`  |
| `is-automated=true`        | 只显示自动构建的镜像        | `docker search -f is-automated=true nginx` |

> [!CAUTION]
>
> `is-automated=true` 已废弃，建议优先使用 `is-official=true` 和 `stars=N` 进行筛选

---

#### 4.docker rmi命令

删除指定镜像

语法：

`docker rmi [OPTIONS] IMAGE [IMAGE...]`

- `[OPTIONS]`   参数
- `IMAGE`   本地镜像对应的哈希值（这里也可以使用镜像名代替）
- `[IMAGE...]`   可连续指定多个镜像

| OPTIONS      | 作用           | 示例                          | 结果                                                         |
| ------------ | -------------- | ----------------------------- | ------------------------------------------------------------ |
| `-f`         | 强制删除       | `docker rmi -f nginx`         | 强制删除nginx镜像                                            |
| `--no-prune` | 不删除下层镜像 | `docker rmi --no-prune nginx` | 只删除指定的镜像本身，如果该镜像是基于其他中间层构建的，那些中间层不会被自动清理（即使现在没有其他镜像使用它们） |

> 特殊用法：
>
> `docker rmi -f $(docker images -q)`
>
> 删除所有镜像

---

#### 5.docker save命令

将一个镜像打包

语法：

`docker save [OPTIONS] IMAGE [IMAGE...]`

- `[OPTIONS]`   参数
- `IMAGE`   本地镜像对应的哈希值（这里也可以使用镜像名代替）
- `[IMAGE...]`   可连续指定多个镜像

| OPTIONS | 作用         | 示例                             | 结果                                     |
| ------- | ------------ | -------------------------------- | ---------------------------------------- |
| `-o`    | 替代标准输出 | `docker save -o nginx.tar nginx` | 将nginx镜像打包为一个名为nginx.tar的文件 |

> 文件必须为`.tar`或`.tar.gz`后缀

---

#### 6.docker load命令

将一个被打包的镜像导入

语法：

`docker load [OPTIONS]`

- `[OPTIONS]`   参数

| OPTIONS | 作用       | 示例                          | 结果                                                 |
| ------- | ---------- | ----------------------------- | ---------------------------------------------------- |
| `-i`    | 指定文件   | `docker load -i nginx.tar`    | 导入指定镜像                                         |
| `-q`    | 不显示过程 | `docker load -q -i nginx.tar` | 导入指定镜像，但是是静默导入，不显示进度条等过程信息 |

> 特殊用法：
>
> `docker load < nginx.tar` 或 `cat nginx.tar | docker load`与`docker load -i nginx.tar`等价

---

#### 7.docker run命令

运行指定docker镜像

语法：

`docker run [OPTIONS] IMAGE [COMMAND] [ARG...]`

- `[OPTIONS]`   参数
- `IMAGE`   本地镜像对应的哈希值（这里也可以使用镜像名代替）
- `[COMMAND]`   容器启动后运行的可执行程序（/bin/bash、python3…），它会覆盖镜像里预设的CMD指令
- `[ARG]`   传递给COMMAND的参数（可以有多个）

| OPTIONS      | 作用                                                         | 示例                                                         | 结果                                                         |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `-d`         | 后台运行容器，不占用当前终端，返回容器 ID                    | `docker run -d nginx:latest`                                 | 容器在后台运行，nginx成功启动服务                            |
| `-it`        | 交互式终端（-i保持 STDIN 打开,-t分配伪终端），通常用来进入容器内部的 Shell | `docker run -it nginx:latest`                                | 前台运行nginx服务，终端被日志输出占用，无法执行其他命令      |
| `--name`     | 给容器指定一个名字，方便后续管理（否则 Docker 会随机生成名字） | `docker run --name nginx1 nginx:latest`                      | 容器启动成功，容器名称为nginx1                               |
| `-p`         | 端口映射，宿主机端口:容器端口，将容器服务暴露到宿主机        | `docker run -p 8081:80 nginx:latest`                         | 该容器的8080端口被映射到宿主机的8081端口，外界通过访问宿主机的8081端口来访问容器内服务 |
| `-P`         | 自动端口映射，将容器内部暴露的端口（EXPOSE）随机映射到宿主机的高位端口 | `docker run -P nginx:latest`                                 | 容器的 80 端口被随机映射到宿主机的高位端口（如 32768）       |
| `-v`         | 挂载卷，将宿主机目录或数据卷挂载到容器内，实现数据持久化或共享 | `docker run -v /host/data:/app/data centos:centos7`          | 现在容器可以访问宿主机的/host/data目录                       |
| `--rm`       | 容器退出后自动删除（适合临时任务，避免遗留已停止的容器）     | `docker run --rm nginx:latest`                               | 容器启动成功，当容器被关闭后会自动删除该容器                 |
| `-e`         | 设置环境变量（键值对），可多次使用                           | `docker run -e MY_ENV=prod -e DEBUG=true ubuntu:20.04 printenv` | 容器内会存在MY_ENV和DEBUG两个环境变量，printenv命令会打印出它们 |
| `--env-file` | 将宿主机上一个文件里的所有环境变量一次性注入到容器中（从Key=Value 格式） | `docker run --env-file /home/pai/project/.env`               | 将.env中的环境变量注入到容器中                               |

---

#### 8.docker exec命令

用于在已经运行中的容器内部执行额外的命令

语法：

`docker exec [OPTIONS] CONTAINER COMMAND [ARG...]`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称
- `COMMAND`   要在容器内执行的命令（如 `/bin/bash`、`ls`、`python app.py` 等）
- `[ARG...]`    传递给COMMAND的参数（可以有多个）

| OPTIONS | 作用                                                         | 示例                                                         | 结果                                                    |
| ------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------- |
| `-it`   | 交互式终端（-i保持 STDIN 打开,-t分配伪终端），通常用来进入容器内部的 Shell | `docker exec -it mycentos /bin/bash`                         | 进入到mycentos容器中（独立进程）                        |
| `-d`    | 后台运行命令，不阻塞当前终端                                 | `docker exec -d mycentos touch /home/pai/hello.exe`          | 后台进入mycentos容器并执行一次touch命令但当前终端无输出 |
| `-e`    | 设置环境变量（仅针对本次执行的命令）                         | `docker exec -e MY_ENV=prod -e DEBUG=true mycentos /bin/bash` | 进入mycentos容器的时候注入环境变量                      |
| `-w`    | 指定进入后所处的工作目录                                     | `docker exec -w /root mycentos /bin/bash`                    | 进入mycentos容器的时候将会直接在/root目录下             |
| `-u`    | 以指定用户名或 UID 执行命令                                  | `docker exec -u root mycentos /bin/bash`                     | 进入mycentos容器的时候将会切换至root身份                |

> [!NOTE]
>
> 1. **容器必须处于 Running 状态**
> 	如果容器已退出（Exited），docker exec会报错。你需要先用 `docker start <容器>` 重新启动它。

---

#### 9.docker attach命令

重新进入已启动的容器

语法：

`docker attach [OPTIONS] CONTAINER`

- `[OPTIONS]`   参数
- `CONTAINER`   容器 ID 或容器名称

> 参数基本用不上

> [!NOTE]
>
> 危险操作：Ctrl+C → 会停止容器
> 安全退出：Ctrl+P Ctrl+Q → 脱离但不停止容器

---

#### 9.docker ps命令

显示所有容器

语法：

`docker ps [OPTIONS]`

- `[OPTIONS]`   参数

| OPTIONS      | 作用                     | 示例                       | 结果                                |
| ------------ | ------------------------ | -------------------------- | ----------------------------------- |
| `-a`         | 显示所有的容器           | `docker ps -a`             | 显示出所有容器                      |
| `-f`         | 显示指定规则所包括的容器 | `docker ps -f "id=abc123"` | 显示出名称为abc123的容器            |
| `-n`         | 显示最新创建的n个容器    | `docker ps -n 3`           | 显示出最新创建的3个容器             |
| `-l`         | 显示最新创建的容器       | `docker ps -l`             | 显示出最新创建的那个容器            |
| `--no-trunc` | 显示完整的CONTAINER ID   | `docker ps --no-trunc`     | 显示出所有容器的完整的CONTAINER ID  |
| `-q`         | 只显示容器的CONTAINER ID | `docker ps -q`             | 只显示出容器的CONTAINER ID （12位） |
| `-s`         | 额外显示容器的大小       | `docker ps -s`             | 显示出所有容器的大小                |

| 过滤器 (Filter)      | 说明                                                         | 示例                                                         |
| :------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| `id`                 | 根据容器的ID进行筛选。                                       | `docker ps --filter "id=abc123"`                             |
| `name`               | 根据容器的名称进行筛选，支持正则表达式。                     | `docker ps --filter "name=my-nginx"` `docker ps --filter "name=^/web_"` (匹配以`/web_`开头的容器) |
| `label`              | 根据容器上的标签（label）进行筛选，可以只写key，也可以写key=value。 | `docker ps --filter "label=version"` `docker ps --filter "label=version=1.0"` |
| `status`             | 根据容器的当前状态进行筛选。                                 | `docker ps --filter "status=exited"` `docker ps --filter "status=running"` |
| `ancestor`           | 根据容器所使用的镜像进行筛选，可以用镜像名、标签或ID。       | `docker ps --filter "ancestor=nginx"` `docker ps --filter "ancestor=ubuntu:18.04"` |
| `before` / `since`   | 筛选出在某个容器之前或之后创建的容器。                       | `docker ps --filter "before=container_1"` `docker ps --filter "since=container_2"` |
| `volume`             | 筛选出挂载了特定数据卷（volume）或绑定挂载（bind mount）的容器。 | `docker ps --filter "volume=/host/path"` `docker ps --filter "volume=my_volume"` |
| `network`            | 筛选出连接到了特定网络的容器。                               | `docker ps --filter "network=my-network"`                    |
| `publish` / `expose` | 筛选出暴露了特定端口的容器。                                 | `docker ps --filter "publish=8080"` `docker ps --filter "expose=3306"` |
| `health`             | 筛选出具有特定健康检查状态的容器。                           | `docker ps --filter "health=healthy"` `docker ps --filter "health=unhealthy"` |
| `exited`             | 筛选出退出码为特定值的容器，通常与`--all`一起使用。          | `docker ps --filter "exited=0"`                              |
| `is-task`            | 筛选出是否为Swarm模式下的任务（Task）容器。                  | `docker ps --filter "is-task=true"`                          |

---

#### 10.docker top命令

查询容器情况

语法：

`docker top CONTAINER`

- `CONTAINER`   容器 ID 或容器名称

---

#### 11.docker start命令

启动容器

语法：

`docker start CONTAINER [CONTAINER...]`

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

---

#### 12.docker restart命令

重启容器

语法：

`docker start [OPTIONS] CONTAINER [CONTAINER...]`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

| OPTIONS | 作用                               | 示例                            | 结果                            |
| ------- | ---------------------------------- | ------------------------------- | ------------------------------- |
| `-t`    | 等待容器优雅停止的时间（默认10秒） | `docker restart -t 20 mycentos` | 名为mycentos的容器会在20s后重启 |

---

#### 13.docker stop命令

关闭容器

语法：

`docker stop [OPTIONS] CONTAINER [CONTAINER...]`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

| OPTIONS | 作用                               | 示例                         | 结果                            |
| ------- | ---------------------------------- | ---------------------------- | ------------------------------- |
| `-t`    | 等待容器优雅停止的时间（默认10秒） | `docker stop -t 20 mycentos` | 名为mycentos的容器会在20s后关闭 |

---

#### 14.docker kill命令

杀死指定容器

语法：

`docker kill [OPTIONS] CONTAINER [CONTAINER...]`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

| OPTIONS | 作用                                                         | 示例                           | 结果                                          |
| :------ | :----------------------------------------------------------- | :----------------------------- | --------------------------------------------- |
| `-s`    | 指定要发送的信号（支持信号名称如 `SIGHUP`，或数字如 `1`），默认是 `SIGKILL` (9) | `docker kill -s KILL mycentos` | 向名为mycentos的容器发送信号9（终止）         |
| `-t`    | （较新版本支持）在发送 `SIGKILL` 强制结束前，等待信号完成处理的超时秒数 | `docker kill -t 30 mycentos    | 杀死名为mycentos的容器，但是给出至多30s的时间 |

| 信号名称    | 作用                                           | 示例                                   | 作用                          |
| :---------- | ---------------------------------------------- | -------------------------------------- | ----------------------------- |
| `TERM` (15) | 礼貌劝退（`docker stop` 默认信号，给时间存盘） | `docker stop -t 30`（根本不用 `-s`）   | 安全关机，给应用存盘时间      |
| `KILL` (9)  | 强制物理断电（不可捕获，`docker kill` 默认）   | `docker kill`（不加 `-s`，默认就是它） | 容器卡死，物理断电            |
| `HUP` (1)   | 重载配置（热更新，进程不退出）                 | docker kill -s HUP                     | 修改了 Nginx/配置文件，热生效 |
| `USR1` (10) | 用户自定义信号1（常用来切日志或打印堆栈）      | docker kill -s USR1                    | 让 Java/Go 应用打印线程堆栈   |
| `STOP` (19) | 暂停进程（不可捕获，类似视频暂停）             | docker kill -s STOP                    | 临时暂停容器进程（类似冻结）  |

---

#### 15.docker logs命令

将应用程序的日志直接打印到标准输出和标准错误输出

语法：

`docker logs [OPTIONS] CONTAINER`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称

| OPTIONS   | 作用                               | 示例                                      | 结果                                 |
| --------- | ---------------------------------- | ----------------------------------------- | ------------------------------------ |
| `-f`      | 实时跟踪日志输出，持续产生新的日志 | `docker logs -f mycentos`                 | 持续显示名为mycentos的容器产生的日志 |
| `-n`      | 显示日志末尾的N行，默认为全部      | `docker logs -n 3 mycentos`               | 显示最后3行的日志                    |
| `--since` | 显示指定时间点后的日志             | `docker logs --since 2026-06-18 mycentos` | 显示2026年6月18日之后的日志          |
| `--until` | 显示指定时间点前的日志             | `docker logs --until 30s mycentos`        | 显示30s前的日志                      |
| `-t`      | 为每条日志添加时间戳               | `docker logs -t mycentos`                 | 在显示日志的时候添加时间戳           |

**1.相对时间**

格式是一个数字加上时间单位：10m(10分钟)、1h30m (1小时30分)、2h (2小时) 等。

```
# 查看过去30分钟的日志
docker logs --since 30m my_container

# 查看从1小时前到30分钟前的日志
docker logs --since 1h --until 30m my_container
```

**2.绝对时间**

- 完整日期时间 (RFC3339)：2026-06-18T14:00:00Z
- 仅日期：2026-06-18
- 高精度时间戳 (RFC3339Nano)：2026-06-18T14:00:00.123456789Z

其他支持的格式包括 2006-01-02T15:04:05、2006-01-02T15:04:05.999999999、2006-01-02Z07:00

```
# 查看2026年6月18日下午2点（UTC）之后的日志
docker logs --since 2026-06-18T14:00:00Z my_container

# 查看2026年6月18日全天的日志
docker logs --since 2026-06-18 --until 2026-06-19 my_container
```

**3.Unix时间戳**

使用自协调世界时（UTC）1970年1月1日午夜以来的秒数。

```
# 查看自Unix时间戳 1718700000 之后的日志
docker logs --since 1718700000 my_container

# 使用纳秒精度
docker logs --since 1718700000.123456789 my_container
```

---

#### 16.docker cp命令

宿主机和容器的文件传输命令

语法：

`docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH|-`

`docker cp [OPTIONS] SRC_PATH|- CONTAINER:DEST_PATH`

- `[OPTIONS]`   参数

- `CONTAINER`   容器 ID 或容器名称
- `SRC_PATH`   容器内的具体路径
- `DEST_PATH`   宿主机上的路径
- `-`   标准输入输出流

| OPTIONS | 作用                     | 示例                                                   | 结果                                                         |
| ------- | ------------------------ | ------------------------------------------------------ | ------------------------------------------------------------ |
| `-a`    | 保留文件和目录的原始属性 | `docker cp -a /home/pai/hello.txt mycentos:/home/pai/` | 宿主机中的hello.txt文件会被发送至容器中，同时保留其原始属性（UID、GID、文件权限、修改时间戳） |
| `-L`    | 识别软链接               | `docker cp -L /home/pai/hello mycentos:/home/pai/`     | 宿主机中的hello为软链接，指向hello.txt文件，命令会直接通过该软链接找到hello.txt文件并发送至容器 |

> 当你把目标路径写成 **`-`** 时，Docker 不会把文件存到硬盘，而是直接把文件的格式流输出到屏幕上（标准输出）。这通常用来配合 `tar` 解压或管道传给其他命令（|、>、>>…）
>
> 输入输出流必须严格遵循 `.tar` 格式

---

#### 17.docker rm命令

删除容器

语法：

`docker rm [OPTIONS] CONTAINER [CONTAINER...]`

- `[OPTIONS]`   参数
- `CONTAINER`   容器 ID 或容器名称（可以是多个）

| OPTIONS | 作用                                         | 示例                    | 结果                                                       |
| ------- | -------------------------------------------- | ----------------------- | ---------------------------------------------------------- |
| `-f`    | 强制删除一个正在运行的容器                   | `docker rm -f mycentos` | 即便名为mycentos的容器依然在运行也会被删除（不加就删不了） |
| `-v`    | 删除容器时，同时删除与该容器关联的匿名数据卷 | `docker rm -v mycentos` | 删除容器时会一并删除那些没有被命名的匿名数据卷             |

---

#### 18.docker inspect命令

查看docker对象（镜像）的详细信息（元数据）

语法：

`docker inspect [OPTIONS] NAME|ID [NAME|ID...]`

- `[OPTIONS]`   参数
- `NAME|ID`   容器名称或镜像名称（可以是多个）

| OPTIONS    | 作用                                                 | 示例                                                         | 结果                       |
| ---------- | ---------------------------------------------------- | ------------------------------------------------------------ | -------------------------- |
| `--format` | 提取指定字段                                         | `docker inspect --format='{{.NetworkSettings.IPAddress}}' mycentos` | 检查容器的IP地址           |
| `-s`       | 显示容器的可写层大小（即该容器占用的额外磁盘空间）   | `docker inscept -s mycentos`                                 | 显示出该镜像的可写层大小   |
| `--type`   | 指定要检查的对象类型（如 container、image、node 等） | `docker inscept --type=image mycentos`                       | 强制检查名为mycentos的镜像 |

| 常用组合                      | 示例                                                         | 作用                               |
| ----------------------------- | ------------------------------------------------------------ | ---------------------------------- |
| 容器 IP 地址                  | `docker inspect --format='{{.NetworkSettings.IPAddress}}' mycentos` | 最常用                             |
| 容器所有端口映射              | `docker inspect --format='{{json .NetworkSettings.Ports}}' mycentos | jq .` | 需要安装 `jq` 工具                 |
| 容器挂载的数据卷              | `docker inspect --format='{{json .Mounts}}' mycentos | jq .` | 查看宿主机路径与容器路径的对应关系 |
| 容器环境变量                  | `docker inspect --format='{{json .Config.Env}}' mycentos | jq .` | 调试启动参数                       |
| 容器当前运行状态              | `docker inspect --format='{{.State.Status}}' mycentos`       | 输出 running / exited 等           |
| 查看完整 JSON（用 jq 格式化） | `docker inspect mycentos | jq .`                             | 比直接输出好看得多                 |

| 对象              | 一句话定义                               | 打个比方                                            | 生命周期                           | 核心特征                                                     |
| :---------------- | :--------------------------------------- | :-------------------------------------------------- | :--------------------------------- | :----------------------------------------------------------- |
| Image（镜像）     | 只读的“模板”或“蓝图”                     | 像面向对象编程中的 类（Class）。                    | 永久静态。一经构建，只读不改       | 不包含状态，不运行进程，占用磁盘静态空间                     |
| Container（容器） | 镜像的“运行实例”                         | 像面向对象编程中 类 实例化后的 对象（Object）。     | 动态临时。可启动、停止、删除、重启 | 有状态（可写层），有进程（PID），有独立的网络和文件系统      |
| Node（节点）      | 运行 Docker 引擎的“物理机/虚拟机/云主机” | 像执行 Java 程序的 JVM 运行环境（即操作系统宿主机） | 集群节点生命周期（加入/离开/下线） | 不仅管单个容器，还参与集群调度（如 Swarm 模式下的工作节点或管理节点） |

---

#### 19.docker export命令

将一个正在运行的容器导出为镜像

语法：

`docker except [OPTIONS] CONTAINER`

- `[OPTIONS]`   参数
- `CONTAINER`   容器 ID 或容器名称

| OPTIONS | 作用         | 示例                               | 结果                                     |
| ------- | ------------ | ---------------------------------- | ---------------------------------------- |
| `-o`    | 替代标准输出 | `docker export -o nginx.tar nginx` | 将nginx镜像打包为一个名为nginx.tar的文件 |

> docker export和docker save最大的区别是前者会将镜像压缩在一起，不包括历史层和元数据，后者则会导出完整的镜像，包括其所有历史层（layers） 和元数据（metadata）

---

#### 20.docker import命令

将一个镜像导入

语法：

`docker import [OPTIONS] file|URL|- [REPOSITORY[:TAG]]`

- `[OPTIONS]`   参数
- `URL`   链接
- `-`   标准输入
- `[REPOSITORY]`   导入后的镜像名（自定义）
- `[:TAG]`   导入后的镜像版本（自定义）

| OPTIONS      | 作用               | 示例                                                         | 结果                                         |
| ------------ | ------------------ | ------------------------------------------------------------ | -------------------------------------------- |
| `-c`         | 应用Dockerfile指令 | `docker import -c "WORKDIR /app" -c "ENV NODE_ENV=production" -c "CMD [\"node\", \"server.js\"]" mycentos.tar centos:mycentos7` | 在导入时设置工作目录、环境变量和默认启动命令 |
| `-m`         | 添加提交信息       | `docker import mycentos.tar centos:mycentos7 -m "我自己设置后的centos7版本"` | 解释本次导入                                 |
| `--platform` | 指定目标平台       | `docker import --platform linux/arm64 mycentos.tar centos:mycentos7` | 指定该镜像需要运行在ARM等非x86架构上         |

---

#### 21.docker system命令

Docker 引擎（服务端）的运维管理命令集

语法：

`docker system COMMAND`

- `COMMAND`   子命令

##### (1)docker system df命令

查看 Docker 占用的磁盘空间分布

语法：

`docker system df [OPTIONS]`

- `[OPTIONS]`   参数

| OPTIONS    | 作用       | 示例                                            | 结果                           |
| ---------- | ---------- | ----------------------------------------------- | ------------------------------ |
| `--format` | 格式化输出 | `docker system df --format "table {{.Images}}"` | 只查看镜像（Images）的使用情况 |
| `-v`       | 详细视图   | `docker system df -v`                           | 显示出详细的磁盘空间分布       |

> `--format`太麻烦了，这边建议使用三剑客处理

##### (2)docker system prune命令

清理所有不再使用的 Docker 对象

语法：

`docker system prune [OPTIONS]`

- `[OPTIONS]`   参数

| OPTIONS     | 作用                                         | 示例                                       | 结果                                             |
| ----------- | -------------------------------------------- | ------------------------------------------ | ------------------------------------------------ |
| `-a`        | 删除悬空镜像的同时删除所有未被容器使用的镜像 | `docker system prune -a`                   | 删除了悬空镜像的同时也删除所有未被容器使用的镜像 |
| `-f`        | 强制删除                                     | `docker system prune -f`                   | 无需手动确认就可以删除                           |
| `--volumes` | 删除所有未被容器使用的数据卷                 | `docker system prune --volumes`            | 所有未被容器使用的数据卷都会被删除               |
| `--filter`  | 条件过滤                                     | `docker system prune --filter "until=24h"` | 删除创建超过24小时的资源                         |

**按标签过滤 (label)**

这个选项非常灵活，可以精细地控制清理范围。它支持两种格式：

- **包含特定标签**：`--filter "label=<key>"` 或 `--filter "label=<key>=<value>"`
- **排除特定标签**：`--filter "label!=<key>"` 或 `--filter "label!=<key>=<value>"`

```
# 1. 清理所有带有 "project=old" 标签的资源
docker system prune --filter "label=project=old"

# 2. 清理所有带有 "deprecated" 标签的资源（无论值是什么）
docker system prune --filter "label=deprecated"

# 3. 清理所有不带 "keep" 标签的资源
docker system prune --filter "label!=keep"

# 4. 清理所有不带 "env=production" 标签的资源
docker system prune --filter "label!=env=production"
```

**按时间过滤 (until)**

这个选项用于清理在指定时间点之前创建的资源。时间格式非常灵活，支持：

- **相对时间**：比如 `10m` (10分钟前)、`1h` (1小时前)、`24h` (24小时前)
- **绝对时间**：比如 `2024-01-01T00:00:00` (RFC3339格式)
- **Unix 时间戳**：比如 `1704067200`

```
# 1. 清理创建/停止时间超过 24 小时的资源
docker system prune --filter "until=24h"

# 2. 清理 2024年1月1日 之前的资源
docker system prune --filter "until=2024-01-01T00:00:00"
```

##### (3)docker system events命令

Docker 的实时事件监控命令

语法：

`docker system events [OPTIONS]`

- `[OPTIONS]`   参数

| OPTIONS    | 作用       | 示例                                           | 结果                 |
| ---------- | ---------- | ---------------------------------------------- | -------------------- |
| `--filter` | 条件过滤   | `docker system events --filter=type=container` | 按类型过滤           |
| `--since`  | 按时间过滤 | `docker system events --since 10m`             | 显示过去10分钟的事件 |
| `--until`  | 按时间过滤 | `docker system events --until 10m`             | 显示10分钟后的事件   |

**时间格式（三种写法通用）**

这两个参数支持三种时间写法，你可以混着用：

- **相对时间（最常用）**：`10m`（10分钟）、`1h`（1小时）、`24h`（24小时）。
- **绝对时间（RFC3339）**：`2024-01-01T00:00:00`（注意要带 `T` 分隔日期和时间）。
- **Unix 时间戳**：`1704067200`（秒数）。

> **时区提醒**：如果不带时区后缀，默认使用**你当前电脑的本地时区**。如果怕乱，可以强制指定 UTC 时区，比如 `2024-01-01T00:00:00Z`
>
> `--since`和`--until`可以连续组合使用

##### (4)docker system info命令

展示 Docker 守护进程（dockerd）本身及其运行环境的整体信息

语法：

`docker system info [OPTIONS]`

- `[OPTIONS]`   参数

> 只有一个-f参数，建议使用三剑客代替处理

---

#### 22.docker pause命令

冻结容器

语法：

`docker pause CONTAINER [CONTAINER...]`

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

---

#### 23.docker unpause命令

取消被docker pause冻结的容器

语法：

`docker unpause CONTAINER [CONTAINER...]`

- `CONTAINER`   容器 ID 或容器名称（可以是多个）

---

#### 24.docker create命令

只创建容器但不运行

语法：

`docker create [OPTIONS] IMAGE [COMMAND] [ARG...]`

- `[OPTIONS]`   参数
- `IMAGE`   本地镜像对应的哈希值（这里也可以使用镜像名代替）
- `[COMMAND]`   容器启动后运行的可执行程序（/bin/bash、python3…），它会覆盖镜像里预设的CMD指令
- `[ARG]`   传递给COMMAND的参数（可以有多个）

| OPTIONS      | 作用                                                         | 示例                                                         | 结果                                                         |
| ------------ | ------------------------------------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `-it`        | 交互式终端（-i保持 STDIN 打开,-t分配伪终端），通常用来进入容器内部的 Shell | `docker create -it nginx:latest`                             | 前台运行nginx服务，终端被日志输出占用，无法执行其他命令      |
| `--name`     | 给容器指定一个名字，方便后续管理（否则 Docker 会随机生成名字） | `docker create --name nginx1 nginx:latest`                   | 容器启动成功，容器名称为nginx1                               |
| `-p`         | 端口映射，宿主机端口:容器端口，将容器服务暴露到宿主机        | `docker create -p 8081:80 nginx:latest`                      | 该容器的8080端口被映射到宿主机的8081端口，外界通过访问宿主机的8081端口来访问容器内服务 |
| `-P`         | 自动端口映射，将容器内部暴露的端口（EXPOSE）随机映射到宿主机的高位端口 | `docker create -P nginx:latest`                              | 容器的 80 端口被随机映射到宿主机的高位端口（如 32768）       |
| `-v`         | 挂载卷，将宿主机目录或数据卷挂载到容器内，实现数据持久化或共享 | `docker create -v /host/data:/app/data centos:centos7`       | 现在容器可以访问宿主机的/host/data目录                       |
| `--rm`       | 容器退出后自动删除（适合临时任务，避免遗留已停止的容器）     | `docker create --rm nginx:latest`                            | 容器启动成功，当容器被关闭后会自动删除该容器                 |
| `-e`         | 设置环境变量（键值对），可多次使用                           | `docker create -e MY_ENV=prod -e DEBUG=true ubuntu:20.04 printenv` | 容器内会存在MY_ENV和DEBUG两个环境变量，printenv命令会打印出它们 |
| `--env-file` | 将宿主机上一个文件里的所有环境变量一次性注入到容器中（从Key=Value 格式） | `docker create --env-file /home/pai/project/.env`            | 将.env中的环境变量注入到容器中                               |

> 它和docker run的区别就是这玩意创建后不启动，所以没有-d选项

---

#### 25.docker history命令



---

---

### 五.Dockerfile指令简介

#### 1.FROM



---

---

### 注解

[^1]: 即 `<none>:<none>` （版本号和DIGEST为空）且被其他镜像依赖的层
