# Render Backend Service Configuration
# Use this when setting up the backend service on Render

## Service Settings
- **Name**: workhub-backend
- **Region**: Oregon (US West) or closest to your users
- **Branch**: main
- **Runtime**: Python 3.11
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Environment Variables
```bash
DATABASE_URL=postgresql://username:password@your-neon-host/workhub?sslmode=require
REDIS_URL=redis://default:password@your-upstash-host:port
SECRET_KEY=your-super-secure-production-secret-key-min-32-chars
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USERNAME=workhub@yourcompany.com
EMAIL_PASSWORD=your-app-specific-password
FROM_EMAIL=workhub@yourcompany.com
FROM_NAME=WorkHub Platform
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
GOOGLE_REDIRECT_URI=https://yourdomain.com/oauth/google/callback
```

## Health Check Configuration
- **Path**: `/health`
- **Timeout**: 30 seconds
- **Interval**: 30 seconds
- **Unhealthy threshold**: 3

## Auto-Deploy
- ✅ Enable auto-deploy from Git
- ✅ Deploy on every push to main branch

## Scaling (for production)
- **Instance Type**: Standard (512MB RAM, 0.5 CPU)
- **Auto-scaling**: Disabled initially (can enable based on usage)

## Custom Domain (Optional)
- Add your domain: `api.yourdomain.com`
- Configure CNAME record: `api.yourdomain.com` → `workhub-backend.onrender.com`