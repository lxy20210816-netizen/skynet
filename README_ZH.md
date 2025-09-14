# 安装n8n
参考：

https://github.com/n8n-io/n8n

最方便的是使用docker部署：
```
docker volume create n8n_data
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
如果后台运行，则把“-it --rm”改为“-d”
```

# 安装mysql


最方便的是使用docker部署：

直接terminal执行：
```
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=testdb \
  -p 3306:3306 \
  mysql:8.0

```

然后在docker desktop上确认运行状态

n8n访问ip，不能写127.0.0.1（因为这是n8n的本地回环地址），应该写本机ip：
```
ifconfig
找到类似 en0 或 wlan0 的网卡下的 IP，比如：
inet 192.168.1.100


```