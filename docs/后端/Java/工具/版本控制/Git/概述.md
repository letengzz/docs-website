# Git 概述

Git是一个免费的，开源的分布式版本控制系统，可以快速高效地处理从小型或大型的各种项目。Git易于学习，占地面积小，性能极快。 它具有廉价的本地库，方便的暂存区域和多个工作流分支等特性。其性能优于Subversion(svn)、CVS、Perforce和ClearCase等版本控制工具。

Git软件比Subversion、CVS、Perforce和ClearCase等SCM(Software Configuration Management软件配置管理)工具具有性价比更高的本地分支、方便的暂存区域和多个工作流等功能。

![image-20230513222149494](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140056182.png)

- GIt官网：https://git-scm.com/

## 区域

Git软件为了更方便地对文件进行版本控制，根据功能得不同划分了三个区域

![image-20230513222510149](https://cdn.jsdelivr.net/gh/letengzz/Two-C@main/img/Java/202305140056005.png)

- **存储区域**：Git软件用于存储资源得区域。一般指得就是.git文件夹
- **工作区域**：Git软件对外提供资源得区域，此区域可人工对资源进行处理。
- **暂存区**：Git用于比对存储区域和工作区域得区域。Git根据对比得结果，可以对不同状态得文件执行操作。

## Git工作机制

![wps6](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202406121215937.jpg)