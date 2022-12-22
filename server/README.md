## 安装

pip install  -r requirements.txt

## 启动
python OcrServer.py


## Linux 后台运行脚本

bash startOcrServer

## 配置修改

修改配置文件service.conf

## 配套插件
chrome-plugin目录

## Linux 错误及解决
### [ImportError: libGL.so](https://www.cnblogs.com/mrneojeep/p/16252044.html) 
- ubuntu

```
apt-get update && apt-get install libgl1
```

-   CentOS、RHEL、Fedora 或其他使用 的 linux 发行版yum

```
yum install mesa-libGL -y
```

