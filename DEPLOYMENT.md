# Comms Platform - Deployment & Hosting Guide

## Issues Fixed ✅

### 1. Session Security
- **Issue**: Users remained logged in even after server restart
- **Fix**: Added session security settings:
  - `SESSION_COOKIE_AGE = 3600` (1 hour timeout)
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`

### 2. Icon Sizes
- All icons reduced from 2-2.5rem to 1.2-1.8rem for elegant appearance
- Updated: Navbar, Login/Signup, Dashboard, Message Form

### 3. Authentication
- Unauthenticated users are now properly redirected to login page
- Sessions expire after 1 hour of inactivity

---

## Deployment with DNS

### Prerequisites
- Domain name (e.g., `yourapp.com`)
- Web server (Nginx or Apache recommended)
- SSL certificate (Let's Encrypt - free)
- Production server (AWS, DigitalOcean, Heroku, etc.)

### Step 1: DNS Configuration
1. Purchase a domain from registrar (GoDaddy, Namecheap, etc.)
2. Point DNS records to your server:
   ```
   A Record: @ → your-server-ip
   A Record: www → your-server-ip
   ```

### Step 2: Prepare Environment
1. Copy `.env.example` to `.env`
   ```bash
   cp .env.example .env
   ```

2. Update `.env` with your domain:
   ```env
   DEBUG=False
   ALLOWED_HOSTS=yourapp.com,www.yourapp.com
   SECRET_KEY=generate-a-secure-key
   RESEND_API_KEY=your-api-key
   ```

### Step 3: Generate Secret Key
```bash
python manage.py shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### Step 4: Install Dependencies
```bash
pip install gunicorn python-dotenv psycopg2-binary
```

### Step 5: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 6: Run Migrations
```bash
python manage.py migrate
```

### Step 7: Nginx Configuration
Create `/etc/nginx/sites-available/comms-platform`:
```nginx
server {
    listen 80;
    server_name yourapp.com www.yourapp.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourapp.com www.yourapp.com;

    ssl_certificate /etc/letsencrypt/live/yourapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourapp.com/privkey.pem;

    client_max_body_size 10M;

    location /static/ {
        alias /path/to/comms_platform/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/comms-platform /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Step 8: SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourapp.com -d www.yourapp.com
```

### Step 9: Systemd Service for Gunicorn
Create `/etc/systemd/system/comms-platform.service`:
```ini
[Unit]
Description=Comms Platform Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/comms_platform
ExecStart=/usr/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 comms_platform.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable comms-platform
sudo systemctl start comms-platform
```

### Step 10: Verify Deployment
1. Visit `https://yourapp.com`
2. Test authentication (login/logout)
3. Check session timeout works

---

## Quick Deployment to FREE Platforms (No Credit Card Required)

### Option 1: PythonAnywhere (RECOMMENDED - Easiest)
✅ **100% FREE** | No credit card needed | Perfect for beginners

#### Step 1: Sign Up
```
1. Go to https://www.pythonanywhere.com/
2. Sign up (free tier available)
3. No credit card needed
```

#### Step 2: Upload Project
```bash
# Via Web Dashboard:
1. Go to Files tab
2. Create new directory: comms_platform
3. Upload project files
```

#### Step 3: Configure Web App
```python
# In Web tab → Add web app → Django
# Select Python 3.8
# Configure WSGI file:

import os
import sys

path = '/home/yourusername/comms_platform'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'comms_platform.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

#### Step 4: Setup Database
```bash
# SSH into PythonAnywhere console:
python manage.py migrate
python manage.py createsuperuser
```

#### Step 5: Update Settings
```python
# In settings.py
ALLOWED_HOSTS = ['yourusername.pythonanywhere.com']
DEBUG = False
```

**Your URL**: `https://yourusername.pythonanywhere.com`

---

### Option 2: Render (FREE Tier Available)
✅ **FREE** | Auto-deploys from GitHub | 500 build minutes/month

#### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/comms_platform.git
git push -u origin main
```

#### Step 2: Deploy on Render
```
1. Go to https://render.com/
2. Sign up with GitHub
3. New → Web Service
4. Connect your GitHub repo
5. Choose Python
```

#### Step 3: Environment Variables
```
DJANGO_SETTINGS_MODULE=comms_platform.settings
PYTHON_VERSION=3.8.10
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.onrender.com
DEBUG=False
RESEND_API_KEY=your-key
```

#### Step 4: Build Command
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

#### Step 5: Start Command
```bash
gunicorn comms_platform.wsgi:application --bind 0.0.0.0:10000
```

**Your URL**: `https://yourdomain.onrender.com`

---

### Option 3: Railway (FREE Tier - $5 Monthly Credit)
✅ **FREE** | $5 free credit monthly | Simple deployment

#### Step 1: Deploy
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

#### Step 2: Add Environment Variables
```
In Railway Dashboard:
DJANGO_SETTINGS_MODULE=comms_platform.settings
SECRET_KEY=your-secret-key
DEBUG=False
```

**Your URL**: Auto-generated like `project-prod-xxxx.railway.app`

---

### Option 4: Fly.io (FREE Tier)
✅ **VERY FREE** | Up to 3 shared VM instances | Good performance

#### Step 1: Install Fly CLI
```bash
# Windows (PowerShell as Admin)
iwr https://fly.io/install.ps1 -useb | iex

# Or use chocolatey
choco install flyctl
```

#### Step 2: Create App
```bash
flyctl launch
# Select Python
# Select yes for Postgres (free tier available)
```

#### Step 3: Deploy
```bash
flyctl deploy
```

#### Step 4: Run Migrations
```bash
flyctl ssh console
python manage.py migrate
python manage.py createsuperuser
exit
```

**Your URL**: `https://yourdomain.fly.dev`

---

### Option 5: Oracle Cloud (ALWAYS FREE)
✅ **TRULY FREE** | Always free tier | No credit card tricks

#### Step 1: Create Account
```
1. Go to https://www.oracle.com/cloud/free/
2. Sign up (free forever tier)
3. Get 2 x Ampere A1 Compute VMs (4 CPU, 24GB RAM total)
```

#### Step 2: Create Compute Instance
```bash
# In Oracle Cloud Console:
1. Compute → Instances → Create Instance
2. Choose Always Free Eligible
3. Ubuntu 22.04 (free)
```

#### Step 3: Setup Server
```bash
ssh -i your-key.key ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip nginx postgresql

# Clone project
git clone your-repo
cd comms_platform

# Install requirements
pip3 install -r requirements.txt

# Setup database
sudo -u postgres createdb comms_platform

# Migrate
python3 manage.py migrate
```

#### Step 4: Configure Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /home/ubuntu/comms_platform/staticfiles/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

#### Step 5: Run App with Gunicorn
```bash
gunicorn --workers 4 --bind 127.0.0.1:8000 comms_platform.wsgi:application &
```

---

## Comparison Table

| Platform | Free Tier | Ease | Speed | Best For |
|----------|-----------|------|-------|----------|
| **PythonAnywhere** | ✅ Free | ⭐⭐⭐⭐⭐ | Medium | Beginners, Quick setup |
| **Render** | ✅ Free | ⭐⭐⭐⭐ | Fast | GitHub projects |
| **Railway** | ✅ $5/mo credit | ⭐⭐⭐⭐ | Fast | Small projects |
| **Fly.io** | ✅ Free | ⭐⭐⭐ | Very Fast | Performance |
| **Oracle Cloud** | ✅ Always Free | ⭐⭐⭐ | Medium | Full control |

---

## RECOMMENDED FOR YOU: PythonAnywhere

**Why PythonAnywhere?**
- ✅ No credit card needed ever
- ✅ Free plan includes free database
- ✅ Web-based file editor
- ✅ Built-in Python console
- ✅ Easy domain mapping
- ✅ Perfect for Django

**Setup Time**: 15 minutes

---

## Quick Deployment Steps (PythonAnywhere)

```bash
# Step 1: Create .env (if needed)
cp .env.example .env

# Step 2: Create requirements.txt
pip freeze > requirements.txt

# Step 3: Add gunicorn
echo "gunicorn" >> requirements.txt
```

Then follow PythonAnywhere setup above.

---

## Adding Custom Domain (All Platforms)

1. **Buy domain**: Namecheap, GoDaddy ($10-15/year)
2. **Point DNS**: Update A record to platform IP
3. **Enable HTTPS**: Automatic with most platforms

### Example for PythonAnywhere
```
In Web app settings:
Security → SSL certificate (auto-generated)
Web → Add domain: yourdomain.com
```



---

## Security Checklist
- [x] Session security configured
- [x] CSRF protection enabled
- [x] XSS filter enabled
- [x] HTTPS/SSL configured
- [x] DEBUG=False in production
- [x] SECRET_KEY changed
- [x] ALLOWED_HOSTS configured
- [ ] Backup database regularly
- [ ] Monitor error logs
- [ ] Set up automated backups

---

## Testing Before Going Live
```bash
# Test production settings
python manage.py check --deploy

# Create superuser for admin
python manage.py createsuperuser

# Test login/logout
# Verify session timeout
# Check email sending
```

---

## Monitoring
Install monitoring tools:
```bash
pip install sentry-sdk  # Error tracking
pip install prometheus-client  # Metrics
```

---

## Questions?
For Heroku: https://devcenter.heroku.com/articles/getting-started-with-django
For Nginx: https://nginx.org/en/docs/
For SSL: https://letsencrypt.org/getting-started/
