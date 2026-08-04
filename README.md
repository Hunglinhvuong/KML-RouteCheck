# 🤖 KML Route Checker Bot

Bot Telegram & Discord để tra cứu tuyến KML, tính tọa độ theo khoảng cách, và hiển thị trên bản đồ.

## 📋 Yêu cầu

- **OS**: Linux (Ubuntu 20.04+, Debian, CentOS, v.v.)
- **Python**: 3.8 trở lên
- **Quyền**: Sudo (để cài đặt service)
- **Token Bot**: Telegram Bot Token từ [@BotFather](https://t.me/BotFather)

## 🚀 Quick Start

### 1. Sao chép project

```bash
git clone <repo-url> ~/kml-route-checker
cd ~/kml-route-checker
```

### 2. Chạy setup tự động

```bash
bash setup.sh
```

Script này sẽ:
- Kiểm tra Python 3
- Tạo virtual environment
- Cài đặt dependencies từ `requirements.txt`
- Xác minh cài đặt

### 3. Cấu hình bot tokens

```bash
# Sao chép template
cp config.env.template config.env

# Chỉnh sửa với token của bạn
nano config.env
```

Cần các thông tin sau:
- `BOT_TOKEN`: Từ [@BotFather](https://t.me/BotFather)
- `ALLOWED_CHAT_IDS`: Chat ID hoặc Group ID
- `DISCORD_TOKEN`: Discord Bot Token (nếu dùng Discord)
- `MYMAP_ID`: Google My Maps ID (tùy chọn)

### 4. Chạy bot

**Chế độ phát triển (foreground)**:
```bash
./run.sh
```

**Chế độ ngầm (background)**:
```bash
nohup ./run.sh > logs/bot.log 2>&1 &
```

## 📦 Cài đặt Service (Systemd)

Để bot chạy tự động khi máy khởi động:

```bash
sudo bash install-service.sh
```

Sau đó quản lý service:

```bash
# Khởi động service
sudo systemctl start kml-route-checker

# Dừng service
sudo systemctl stop kml-route-checker

# Xem trạng thái
sudo systemctl status kml-route-checker

# Xem logs real-time
sudo journalctl -u kml-route-checker -f

# Restart service
sudo systemctl restart kml-route-checker

# Vô hiệu hóa auto-start
sudo systemctl disable kml-route-checker
```

## 📁 Cấu trúc Project

```
├── bot/                    # Bot handlers (Telegram, Discord)
│   ├── __init__.py
│   ├── telegram_bot.py     # Telegram bot implementation
│   └── discord_bot.py      # Discord bot implementation
├── core/                   # Lõi xử lý logic
│   ├── kml_reader.py       # Đọc file KML
│   ├── geo_calc.py         # Tính toán tọa độ geodesic
│   ├── route_manager.py    # Quản lý danh sách tuyến
│   └── map_link.py         # Tạo link Google Maps
├── data/                   # Thư mục chứa file KML tuyến
├── utils/                  # Tiện ích
│   ├── message_guard.py    # Kiểm tra độ dài tin nhắn
│   └── pathing.py          # Quản lý đường dẫn (cross-platform)
├── tests/                  # Unit tests
├── config.env              # Cấu hình token (được Git ignore)
├── config.env.template     # Template cấu hình
├── requirements.txt        # Python dependencies
├── run.py                  # Entry point chính
├── run.sh                  # Launch script Linux
├── setup.sh                # Setup script tự động
├── install-service.sh      # Script cài systemd service
└── README.md              # File này
```

## 🔧 Troubleshooting

### Bot không khởi động

1. Kiểm tra token trong `config.env`:
```bash
cat config.env | grep BOT_TOKEN
```

2. Kiểm tra logs:
```bash
# Nếu chạy qua systemd
sudo journalctl -u kml-route-checker -n 50

# Nếu chạy qua run.sh
./run.sh 2>&1 | tail -20
```

3. Kiểm tra virtual environment:
```bash
source .venv/bin/activate
python -c "import telegram; print('OK')"
```

### Port hoặc permission bị từ chối

```bash
# Kiểm tra quyền thư mục
ls -la

# Nếu cần, cấp quyền thực thi
chmod +x run.sh setup.sh install-service.sh
```

### Module không tìm thấy

```bash
# Cài đặt lại dependencies
source .venv/bin/activate
pip install -r requirements.txt --force-reinstall
```

## 📊 Kiểm tra chức năng

```bash
# Chạy tests
source .venv/bin/activate
python -m pytest tests/ -v

# Kiểm tra đọc KML
python - <<'EOF'
from core.kml_reader import read_route_from_kml
from utils.pathing import resolve_data_path
path = resolve_data_path('CSG11.NA_DCU_CAU_BUNG$NA_DCU_DIEN_HONG.kml')
route = read_route_from_kml(path)
print(f'✅ Route có {len(route)} điểm')
EOF
```

## 🔄 Cập nhật Project

Khi có cập nhật từ repository:

```bash
git pull origin main
bash setup.sh                 # Cài lại dependencies nếu thay đổi
sudo systemctl restart kml-route-checker  # Restart service
```

## 📝 Logs & Monitoring

### Xem logs thực time (systemd)

```bash
sudo journalctl -u kml-route-checker -f --lines=50
```

### Lưu logs vào file

```bash
mkdir -p logs
sudo journalctl -u kml-route-checker --no-pager > logs/bot.log
```

### Kiểm tra resource usage

```bash
ps aux | grep run.py
systemctl status kml-route-checker
```

## 💡 Tips

1. **Tạo alias** cho lệnh hay dùng:
```bash
alias bot-start='sudo systemctl start kml-route-checker'
alias bot-stop='sudo systemctl stop kml-route-checker'
alias bot-log='sudo journalctl -u kml-route-checker -f'
```

2. **Backup config**:
```bash
cp config.env config.env.backup
```

3. **Auto-restart nếu crash**:
   - Systemd service đã có `Restart=always` built-in

4. **Chạy trên Docker** (nếu muốn):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN bash setup.sh
CMD ["./run.sh"]
```

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra logs: `sudo journalctl -u kml-route-checker -n 100`
2. Kiểm tra cấu hình: `cat config.env`
3. Chạy tests: `python -m pytest tests/ -v`
4. Xem commit logs: `git log --oneline -10`

---

**Phiên bản**: 1.0.0  
**Cập nhật lần cuối**: 2026-07-01  
**Hỗ trợ Python**: 3.8+
