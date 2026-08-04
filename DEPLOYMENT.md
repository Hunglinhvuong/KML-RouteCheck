# 📖 Deployment Guide - KML Route Checker Bot

Hướng dẫn chi tiết để triển khai bot trên các máy Linux khác nhau.

## 🎯 Phương án triển khai

### 1. Triển khai trực tiếp (Bare Metal)
### 2. Triển khai qua Systemd Service
### 3. Triển khai qua Docker

---

## Phương án 1: Triển khai Trực tiếp

**Khi dùng**: Phát triển, test, hoặc máy chủ đơn giản

### Bước 1: Transfer project

```bash
# Từ máy local
scp -r /path/to/kml-route-checker user@remote-server:/home/user/

# Hoặc dùng git
ssh user@remote-server
git clone https://github.com/your-repo/kml-route-checker.git
cd kml-route-checker
```

### Bước 2: Setup

```bash
cd ~/kml-route-checker
bash setup.sh
```

### Bước 3: Cấu hình token

```bash
nano config.env
# Nhập BOT_TOKEN, ALLOWED_CHAT_IDS, v.v.
```

### Bước 4: Chạy

```bash
# Terminal 1 - chạy trực tiếp
./run.sh

# Hoặc chạy ở background
nohup ./run.sh > logs/bot.log 2>&1 &

# Lưu process ID
echo $! > bot.pid
```

### Dừng bot

```bash
kill $(cat bot.pid)
```

---

## Phương án 2: Triển khai Systemd Service

**Khi dùng**: Máy chủ production, cần auto-restart, monitoring

### Bước 1: Transfer & Setup

```bash
# Transfer project
scp -r /path/to/kml-route-checker user@remote-server:/opt/

# SSH vào server
ssh user@remote-server
cd /opt/kml-route-checker

# Setup
bash setup.sh
```

### Bước 2: Cấu hình

```bash
sudo nano config.env
```

### Bước 3: Cài service

```bash
sudo bash install-service.sh
```

Script sẽ:
- Tạo user `telebot`
- Tạo service file `/etc/systemd/system/kml-route-checker.service`
- Enable service để auto-start

### Bước 4: Quản lý service

```bash
# Khởi động
sudo systemctl start kml-route-checker

# Xem trạng thái
sudo systemctl status kml-route-checker

# Xem logs real-time
sudo journalctl -u kml-route-checker -f

# Dừng
sudo systemctl stop kml-route-checker

# Restart
sudo systemctl restart kml-route-checker
```

### Lợi ích

✅ Auto-restart khi crash  
✅ Auto-start khi boot  
✅ Logs tập trung (journald)  
✅ Quản lý quyền an toàn  
✅ Dễ monitor & upgrade  

---

## Phương án 3: Triển khai Docker

**Khi dùng**: Môi trường cloud, multiple servers, horizontal scaling

### Bước 1: Chuẩn bị

```bash
# Cài Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Cài Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Bước 2: Transfer project

```bash
scp -r /path/to/kml-route-checker user@remote-server:/home/user/
ssh user@remote-server
cd ~/kml-route-checker
```

### Bước 3: Cấu hình

```bash
cp config.env.template .env
nano .env
# Nhập các token
```

### Bước 4: Khởi động container

```bash
# Kiểm tra Docker setup
docker --version
docker-compose --version

# Build & run
docker-compose up -d

# Kiểm tra status
docker-compose ps

# Xem logs
docker-compose logs -f

# Dừng
docker-compose down
```

### Các lệnh hay dùng

```bash
# Rebuild image
docker-compose up -d --build

# Xem logs của bot
docker-compose logs -f kml-bot

# SSH vào container
docker-compose exec kml-bot bash

# Check health
docker-compose ps
docker stats kml-bot

# Restart service
docker-compose restart kml-bot

# Xóa container & volumes
docker-compose down -v
```

### Lợi ích

✅ Environment isolation  
✅ Portable across systems  
✅ Easy to scale  
✅ Version control  
✅ Cloud-ready (AWS, GCP, Azure)  

---

## 📊 So sánh các phương án

| Tiêu chí | Bare Metal | Systemd | Docker |
|---------|-----------|---------|--------|
| **Độ phức tạp** | Thấp | Trung bình | Cao |
| **Performance** | Cao | Cao | Trung bình |
| **Auto-restart** | ❌ | ✅ | ✅ |
| **Portability** | Thấp | Trung bình | Cao |
| **Scaling** | Khó | Khó | Dễ |
| **Monitoring** | Manual | Built-in | Docker native |
| **Development** | ✅ | ⚠️ | ✅ |
| **Production** | ⚠️ | ✅ | ✅✅ |

---

## 🔄 Migration từ phương án này sang phương án khác

### Bare Metal → Systemd

```bash
# 1. Stop bare metal instance
kill $(cat bot.pid)

# 2. Setup systemd
sudo bash install-service.sh

# 3. Start service
sudo systemctl start kml-route-checker
```

### Systemd → Docker

```bash
# 1. Stop systemd service
sudo systemctl stop kml-route-checker

# 2. Copy config.env
cp /opt/kml-route-checker/config.env ~/.env

# 3. Transfer project
cp -r /opt/kml-route-checker ~/kml-route-checker

# 4. Start with Docker
docker-compose up -d
```

---

## 🔐 Bảo mật

### 1. Bảo vệ config.env

```bash
# Chỉ owner có thể đọc
chmod 600 config.env

# SSH key-based auth
ssh-keygen -t ed25519
ssh-copy-id user@remote-server
```

### 2. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp  # SSH only
sudo ufw enable
```

### 3. Backup token

```bash
# Backup config.env riêng (lưu ở nơi an toàn)
bash backup.sh /safe/location/
```

### 4. Docker Security

```bash
# Run as non-root (already in Dockerfile)
# Scan image
docker scan kml-bot:latest

# Use secrets management
docker secret create bot_token -
# Enter token, then Ctrl+D
```

---

## 📈 Monitoring & Logging

### Systemd

```bash
# Real-time logs
sudo journalctl -u kml-route-checker -f

# Last 100 lines
sudo journalctl -u kml-route-checker -n 100

# Since last boot
sudo journalctl -u kml-route-checker -b

# Export to file
sudo journalctl -u kml-route-checker > bot-logs.txt
```

### Docker

```bash
# Logs
docker-compose logs -f --tail=50 kml-bot

# Stats
docker stats kml-bot

# Health check
docker inspect --format='{{json .State.Health}}' kml_route_checker
```

### System Monitor

```bash
# Resource usage
ps aux | grep run.py
htop

# Network
netstat -tuln | grep LISTEN

# Disk
df -h
du -sh data/
```

---

## 🚨 Troubleshooting Deployment

### Bot không khởi động

```bash
# 1. Check logs
sudo journalctl -u kml-route-checker -n 50

# 2. Verify config
cat config.env | grep BOT_TOKEN

# 3. Test token
python -c "
from telegram import Bot
from telegram.error import InvalidToken
try:
    bot = Bot(token='YOUR_TOKEN')
    bot.get_me()
    print('✅ Token valid')
except InvalidToken:
    print('❌ Invalid token')
"

# 4. Check permissions
ls -la /opt/kml-route-checker/
ls -la config.env
```

### Port bị chiếm

```bash
# Kiểm tra port (nếu bot dùng port cụ thể)
sudo lsof -i :PORT_NUMBER

# Kill process
sudo kill -9 PID
```

### Memory leak

```bash
# Monitor memory
watch -n 1 'ps aux | grep run.py | grep -v grep'

# Limit memory (systemd)
# Thêm vào service file:
# MemoryLimit=512M
```

### Disk space

```bash
# Check
df -h

# Clean logs
sudo journalctl --vacuum=30d
rm -rf logs/old_*.log
```

---

## ✅ Checklist Deployment

- [ ] Transfer project complete
- [ ] Setup script ran successfully
- [ ] config.env filled with real tokens
- [ ] Bot started successfully
- [ ] Bot responds to commands
- [ ] Logs accessible
- [ ] Backup tested
- [ ] Service configured (nếu dùng systemd)
- [ ] Auto-start verified
- [ ] Monitoring set up

---

## 📝 Maintenance

### Daily

```bash
# Check status
sudo systemctl status kml-route-checker

# Check logs for errors
sudo journalctl -u kml-route-checker -p err
```

### Weekly

```bash
# Backup data
bash backup.sh /backup/location/

# Check disk space
df -h
```

### Monthly

```bash
# Update dependencies
source .venv/bin/activate
pip install -U -r requirements.txt

# Restart service
sudo systemctl restart kml-route-checker
```

---

## 🔗 Tài liệu liên quan

- [README.md](README.md) - Overview & Quick Start
- [requirements.txt](requirements.txt) - Dependencies
- [config.env.template](config.env.template) - Configuration template
- [Dockerfile](Dockerfile) - Docker image definition
- [docker-compose.yml](docker-compose.yml) - Compose configuration

---

**Phiên bản**: 1.0.0  
**Cập nhật**: 2026-07-01
