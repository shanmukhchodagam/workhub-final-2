# Render AI Agent Service Configuration
# Use this when setting up the AI agent service on Render

## Service Settings
- **Name**: workhub-agent
- **Region**: Oregon (US West) or same as backend
- **Branch**: main
- **Runtime**: Python 3.11
- **Build Command**: `cd langgraph && pip install -r requirements.txt`
- **Start Command**: `cd langgraph && python main.py`

## Environment Variables
```bash
DATABASE_URL=postgresql://username:password@your-neon-host/workhub?sslmode=require
REDIS_URL=redis://default:password@your-upstash-host:port
BACKEND_URL=https://workhub-backend.onrender.com
GROQ_API_KEY=your-groq-api-key
PYTHONUNBUFFERED=1
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
- **Auto-scaling**: Disabled initially (can enable based on AI usage)

## Custom Domain (Optional)
- Add your domain: `agent.yourdomain.com`
- Configure CNAME record: `agent.yourdomain.com` → `workhub-agent.onrender.com`