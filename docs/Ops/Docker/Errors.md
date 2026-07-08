# Docker 常见错误

> deploying WSL2 distributions provisioning docker WSL distros: ensuring main distro is deployed: checking if main distro is up to date: checking main distro bootstrap version: getting main distro bootstrap version: exit code: 4294967295: running WSL command wsl.exe C:\WINDOWS\System32\wsl.exe -d docker-desktop -u root -e wsl-bootstrap version: 无法将磁盘“ HOME \AppData\Local\Docker\wsl\distro\ext4.vhdx”附加到 WSL2： 系统找不到指定的路径。 Error code: Wsl/Service/CreateInstance/MountVhd/HCS/ERROR_PATH_NOT_FOUND : exit status 0xffffffff checking if isocache exists: CreateFile \\wsl$\docker-desktop-data\isocache\: The network name cannot be found.

解决方法

1. 打开管理员终端，运行`wsl --list`命令获取所有wsl分发：

   ```shell
   wsl --list
   ```

2. 运行`wsl --unregister docker-desktop-data`命令：

   ```shell
   wsl --unregister docker-desktop-data
   ```

3. 运行`wsl --unregister docker-desktop`命令：

   ```shell
   wsl --unregister docker-desktop
   ```

4. 重启docker-desktop即可

![image-20240924230323719](assets/img202409242303966.png)
