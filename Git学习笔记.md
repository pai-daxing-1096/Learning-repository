# Git学习笔记

---

## 一. 常用指令

### 1. git status
查看当前工作区和暂存区的文件状态（已修改、已暂存、未跟踪等）。

```bash
git status
```

### 2. git add

将文件添加到暂存区（Staging Area），准备提交。

```
git add 文件名                # 添加单个文件
git add 文件名1 文件名2 ...   # 添加多个文件
git add .                     # 添加当前目录下所有更改（包括新文件、修改、删除）
git add -A                    # 添加整个仓库的所有更改（包括根目录）
```

### 3. git reset

**取消暂存**（unstage）文件，但保留工作区的修改。

```
git reset                    # 取消所有文件的暂存状态（保留工作区修改）
git reset 文件名              # 取消指定文件的暂存状态
git reset 文件名1 文件名2 ... # 取消多个文件
git reset *.txt              # 使用通配符取消匹配的文件
git reset 文件夹名/           # 取消该文件夹下所有文件的暂存
```

### 4. git commit

将暂存区的改动提交到本地仓库，形成一次版本记录。

```
git commit -m "提交说明"       # 直接写说明
git commit                    # 会打开编辑器让你写多行说明
git commit -am "说明"          # 跳过 add 步骤（仅对已跟踪文件有效）
```

---

## 二. 版本回退与前进

### 1. git log

查看提交历史，找到你想回退的版本号（commit hash）。

```
git log                  # 完整历史
git log --oneline        # 简洁一行显示（最常用）
git log --graph --oneline  # 以图形方式显示分支合并
git log --pretty=online   # 注意：正确写法是 --pretty=oneline（上面有更好用的 --oneline）
```

### 2. git reset –hard

**强硬回退**：将当前分支、暂存区、工作区**全部**重置到指定版本。
⚠️ 会丢弃该版本之后的所有修改，慎用。

```
git reset --hard 版本提交编号   # 回到指定版本（之后提交全丢失）
git reset --hard HEAD~2        # 回到两个提交之前
```

其他 reset 模式：

- `git reset --soft 版本号` ：只移动分支指针，暂存区和工作区保留（相当于撤销 commit，但保留改动）
- `git reset --mixed 版本号`（默认）：移动分支指针，重置暂存区，但保留工作区修改

### 3. git reflog

**救命命令**：记录你在本地所有 HEAD 的移动。即使用 `git reset --hard` 丢失了提交，也能找回。

```
git reflog
# 输出类似：e442f37 (HEAD -> main) HEAD@{0}: reset: moving to e442f37
#          a1b2c3d HEAD@{1}: commit: 新的功能
```

找到目标版本的 hash，再用 `git reset --hard 那个hash` 就能回去。

### 4. git revert

**安全回退**：通过创建一个**新提交**来撤销某次历史提交，不破坏历史。
适合多人协作时撤销已经 push 的错误提交。

```
git revert 版本提交编号   # 撤销那次提交的所有改动，并生成一个新的撤销 commit
```

------

## 三. 远程仓库操作

### 1. git clone

将远程仓库完整克隆到本地（包含所有历史）。

```
git clone 线上仓库地址                    # 默认目录名为仓库名
git clone 线上仓库地址 自定义文件夹名       # 指定本地文件夹名
git clone -b 分支名 线上仓库地址           # 克隆指定分支
```

### 2. git remote

管理远程仓库别名。

```
git remote -v                # 列出所有远程仓库及其地址
git remote add origin 地址   # 添加一个名为 origin 的远程仓库
git remote remove origin     # 删除 origin
git remote set-url origin 新地址  # 修改远程地址
```

### 3. git push

将本地提交推送到远程仓库。

```
git push origin main                # 将本地 main 分支推送到远程 origin 的 main 分支
git push -u origin main             # 推送并设置上游（以后直接 git push 即可）
git push origin 本地分支名:远程分支名  # 推送不同名的分支
git push --delete origin 分支名      # 删除远程分支
```

**当遇到 non-fast-forward 错误时**（远程有本地没有的提交）：

- 先用 `git pull` 合并，再 push

- 如果确定要覆盖远程（例如个人练习），用强制推送：

	```
	git push --force-with-lease origin main   # 更安全：检查远程是否被他人更新过
	git push --force origin main              # 野蛮覆盖（可能丢别人代码）
	```

### 4. git fetch / git pull

从远程获取更新。

```
git fetch origin                # 下载远程最新数据，但不合并（只更新 remote 分支）
git fetch origin main           # 只 fetch 某个分支
git pull origin main            # fetch + merge （常用）
git pull --rebase origin main   # fetch + rebase （保持线性历史，推荐）
```

------

## 四. 分支管理

### 1. git branch

查看、创建、删除分支。

```
git branch             # 列出所有本地分支，当前分支前有 * 标记
git branch -r          # 列出远程分支
git branch -a          # 列出所有分支（本地+远程）
git branch 新分支名     # 创建新分支（但不会切换过去）
git branch -d 分支名    # 删除已合并的分支
git branch -D 分支名    # 强制删除未合并的分支
```

### 2. git switch / git checkout

**切换分支**（新项目推荐使用 `git switch`）。

```
git switch 分支名             # 切换到一个已存在的分支
git switch -c 新分支名        # 创建并切换到新分支
git switch -                  # 切换到上一个分支

# 老式写法（依然可用，但不推荐新学）
git checkout 分支名
git checkout -b 新分支名
```

### 3. git merge

合并分支：将指定分支的改动合并到当前分支。

```
git merge 被合并的分支名          # 默认会创建 merge commit
git merge --no-ff 被合并的分支名  # 强制创建 merge commit（保留分支历史）
```

### 4. git branch – 设置上游

本地分支与远程分支建立关联。

```
git branch -u origin/远程分支名   # 当前分支追踪远程分支
git branch -vv                  # 查看所有分支的上游关系
```

------

## 五. 冲突的产生与解决

### 场景

当两个分支修改了同一文件的同一区域，且你执行 `git merge` 或 `git pull` 时，Git 无法自动合并，就会产生冲突。

### 解决步骤

1. 执行 `git merge 分支B` 或 `git pull`，屏幕会提示冲突文件。

2. 打开冲突文件，Git 已用 `<<<<<<<`、`=======`、`>>>>>>>` 标记出冲突区域。

	```
	<<<<<<< HEAD
	你的当前分支内容
	=======
	对方分支的内容
	>>>>>>> 分支B
	```

3. 手动编辑文件，删除冲突标记，保留最终想要的内容。

4. 保存文件后执行：

	```
	git add 冲突文件
	git commit -m "resolve conflict"
	```

	（merge 会自动生成合并信息，也可直接 `git commit` 使用默认信息）

### 避免冲突的小技巧

- 频繁 `git pull` 或 `git fetch`，减少分支落后幅度。
- 在专用分支上开发，完成后再合并到主分支。
- 使用 `git pull --rebase` 保持线性历史，但遇到冲突时解决步骤略不同（需 `git rebase --continue`）。

------

## 六. 其他实用命令

### 1. git diff

查看文件之间的差异。

```
git diff                     # 工作区 vs 暂存区
git diff --staged            # 暂存区 vs 最近一次 commit
git diff HEAD                # 工作区 vs 最近一次 commit
git diff 分支1 分支2          # 两个分支的差异
git diff 版本号1 版本号2      # 两个提交的差异
```

### 2. git stash

临时保存工作区未提交的修改，让工作区变干净。

```
git stash                    # 保存当前修改（包括暂存区）
git stash save "描述信息"     # 带说明的保存
git stash list               # 列出所有 stash
git stash pop                # 应用最近的 stash 并删除它
git stash apply              # 应用最近的 stash 但不删除
git stash drop stash@{0}     # 删除指定 stash
```

### 3. git tag

给某个提交打一个永久的标签（常用于版本发布）。

```
git tag                       # 列出所有标签
git tag v1.0                  # 给当前 commit 打轻量标签
git tag -a v1.0 -m "发布版"    # 附注标签（推荐）
git tag v1.0 版本号            # 给历史 commit 打标签
git push origin v1.0          # 推送单个标签
git push origin --tags        # 推送所有本地标签
```

### 4. git rm

从 Git 仓库和工作区中删除文件（相当于 `rm` + `git add`）。

```
git rm 文件名          # 删除文件并记录到暂存区
git rm --cached 文件名 # 仅从仓库删除，但保留工作区文件（适用于误 add 的文件）
```

------

## 七. 常见问题速查表

| 你想要做什么                  | 命令                                                         |
| :---------------------------- | :----------------------------------------------------------- |
| 放弃工作区某个文件的修改      | `git restore 文件名`                                         |
| 取消暂存（不删文件改动）      | `git restore --staged 文件名` 或 `git reset 文件名`          |
| 修改最后一次提交的说明        | `git commit --amend -m "新说明"`                             |
| 不小心把文件 add 了想 remove  | `git rm --cached 文件名`                                     |
| 撤销刚刚的 commit（保留修改） | `git reset --soft HEAD~1`                                    |
| 彻底回到某个历史版本（风险）  | `git reset --hard 版本号`                                    |
| 撤销历史上某次提交（安全）    | `git revert 版本号`                                          |
| 合并分支时不想处理了          | `git merge --abort`                                          |
| 放弃所有未提交的修改          | `git restore .`（工作区）+ `git clean -fd`（删除未跟踪文件） |

------

> 📌 提示：大部分命令都可以用 `git 命令 --help` 查看详细文档，或在终端中按 `q` 退出日志视图。
