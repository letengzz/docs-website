# NVM

nvm(`Node Version Manager`) 顾名思义它是用来管理 node 版本的工具，方便切换不同版本的 Node.js

![image-20231026210145778](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310262101265.png)

## 下载安装

下载地址 https://github.com/coreybutler/nvm-windows/releases， 选择 nvm-setup.exe 下载即可

## 使用

![image-20231026211330164](https://cdn.jsdelivr.net/gh/letengzz/tc2/img202310262113854.png)

**说明**：安装nvm后需要执行`nvm use xxx` 进行安装，否则node 和 npm命令无法使用

如果已经执行了上述命令但还是报node不是内部命令，那么先检查  C:\Program Files\nodejs文件是否可用，一般来说应该是不可用的，删除即可。

打开nvm文件夹，在nvm下面建一个文件夹nodejs，这个nodejs文件夹下面不要放任何东西，保持为空即可。

高级系统设置环境变量NVM_SYMLINK路径都改成自己node的所在路径，设置好之后请务必关掉终端后，再打开。总之一定要重新进cmd

此时，进到终端执行`node -v`估计还是之前的样子，此时需要先  `nvm uninstall v10.15.3`（上面安装的nodejs），也就是最好卸载掉之前用nvm安装的node，然后再重新安装你所需要的各种版本的node。

安装好node后，使用 `nvm use [your node version]`

此时执行`node -v`，就正常显示版本了。
