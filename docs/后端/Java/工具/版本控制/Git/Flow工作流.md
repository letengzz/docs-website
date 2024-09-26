# Git Flow工作流

在项目开发过程中使用 Git 的方式常见的有：

- 集中式工作流
- 功能开发工作流
- GitFlow工作流
- Forking工作流

## 集中式工作流

所有修改都提交到 Master 这个分支。比较适合极小团队或单人维护的项目，不建议使用这种方式。

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132336755.jpg) 

## 功能开发工作流

功能开发应该在一个专门的分支，而不是在 master 分支上。适用于小团队开发。

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132336286.jpg) 

## GitFlow工作流

公司中最常用于管理大型项目。为功能开发、发布准备和维护设立了独立的分支，让发布迭代过程更流畅。

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132336887.jpg) 

## Forking工作流

在 GitFlow 基础上，充分利用了 Git 的 Fork 和 pull request 的功能以达到代码审核的目的。一般用于跨团队协作、网上开源项目。

![img](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406132336430.jpg) 

## 