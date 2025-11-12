# Git学习笔记

---

## 一.常用指令

### 1.git status

查看当前的文件操作状态

语法：`git status`

### 2.git add

将文件添加到暂存区

语法：`git add`

拓展：

- `git add 文件名`
	- 添加文件至缓存区
- `git add 文件名1 文件名2 文件名3 ...` 
	- 添加多个文件至缓存区
- `git add .`
	- 将当前目录所有文件添加至缓存区

### 3.git reset

取消所有文件的暂存状态

语法：`git reset`

拓展：

- `git reset 文件名`
	- 取消指定文件的暂存状态
- `git reset 文件名1 文件名2 文件名3 ...`
	- 取消多个指定文件的暂存状态
- `git reset *文件后缀`
	- 结合通配符取消匹配到的文件的暂存状态
- `git reset 文件夹名/`
	- 取消指定文件夹下的所有文件的暂存状态

### 4.git commit -m

将文件提交至仓库

语法：`git commit -m "注释内容"`

### 5.source

刷新状态重新读取

语法：`source 文件路径`

---

## 二.版本回退

### 1.git log

查看修改的版本

语法：`git log`

拓展：

- `git log --pretty=online`
	- 查询出的界面更为简洁明了

### 2.git reset –hard 

退回指定的版本

语法：`git reset --hard 版本提交编号`

### 3.git reflog

回到曾经的版本后，查看历史记录以获得新版本的版本提交编号

语法：`git reflog`

---

## 三.远程仓库

### 1.git clone

将远程仓库克隆至本地仓库

语法：`git clone 线上仓库地址`

### 2.git push

将文件推送至远程仓库

语法：`git push` 

---

## 四.分支相关指令

### 1.git branch

查看分支状态

语法：`git branch`

其中`*`标记的分支为当前分支

###  2.git branch

创建分支

语法：`git branch 分支名`

### 3.git checkout

切换分支

语法：`git checkout 分支名`

### 4.git branch -d

删除分支

语法：`git branch -d 分支名`

### 5.git merge

合并分支

语法：`git merge 被合并的分支名`

---

## 五.冲突的产生与解决

### 1.git pull

将远程仓库的文件与本地仓库的文件合并，主要在`git push`之前使用，防止发生冲突





