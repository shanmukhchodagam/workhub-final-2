# WorkHub Deployment Checklist ✅

## Pre-Deployment Setup

### 1. Environment Configuration
- [ ] Copy `.env.production.example` to `.env.production`
- [ ] Fill in all required environment variables:
  - [ ] `DATABASE_URL` (Neon PostgreSQL)
  - [ ] `REDIS_URL` (Upstash Redis)
  - [ ] `SECRET_KEY` (32+ character random string)
  - [ ] `GROQ_API_KEY` (from Groq console)
  - [ ] Email configuration (SMTP settings)
  - [ ] Google OAuth credentials
- [ ] Verify all URLs and endpoints are correct

### 2. Database Setup (Neon)
- [ ] Create Neon project and database
- [ ] Note down connection string with SSL
- [ ] Run database migrations: `python backend/migrate_database.py`
- [ ] Verify tables are created correctly
- [ ] Test database connectivity

### 3. Redis Setup (Upstash)
- [ ] Create Upstash Redis instance
- [ ] Configure with TLS enabled
- [ ] Note down connection string
- [ ] Test Redis connectivity

### 4. Code Preparation
- [ ] Ensure all code is committed to Git
- [ ] Run local tests to verify functionality
- [ ] Check that health endpoints work locally
- [ ] Verify environment variables are properly loaded

## Platform-Specific Deployment

### 5. Backend Deployment (Render)
- [ ] Connect GitHub repository to Render
- [ ] Create new Web Service
- [ ] Configure service settings:
  - [ ] Name: `workhub-backend`
  - [ ] Runtime: Python 3.11
  - [ ] Build command: `pip install -r requirements.txt`
  - [ ] Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Add environment variables
- [ ] Enable auto-deploy from main branch
- [ ] Deploy and verify service starts successfully
- [ ] Test health endpoint: `https://workhub-backend.onrender.com/health`

### 6. AI Agent Deployment (Render)  
- [ ] Create second Web Service on Render
- [ ] Configure service settings:
  - [ ] Name: `workhub-agent`
  - [ ] Runtime: Python 3.11
  - [ ] Build command: `cd langgraph && pip install -r requirements.txt`
  - [ ] Start command: `cd langgraph && python main.py`
- [ ] Add environment variables
- [ ] Enable auto-deploy from main branch
- [ ] Deploy and verify service starts successfully
- [ ] Test health endpoint: `https://workhub-agent.onrender.com/health`

### 7. Frontend Deployment (Vercel)
- [ ] Connect GitHub repository to Vercel
- [ ] Configure project settings:
  - [ ] Framework: Next.js
  - [ ] Root directory: `frontend`
  - [ ] Node.js version: 20.x
- [ ] Add environment variables:
  - [ ] `NEXT_PUBLIC_API_URL`
  - [ ] `NEXT_PUBLIC_WS_URL`
- [ ] Enable auto-deploy from main branch
- [ ] Deploy and verify build succeeds
- [ ] Test frontend accessibility: `https://workhub.vercel.app`

## Post-Deployment Verification

### 8. Integration Testing
- [ ] Test user registration/login flow
- [ ] Verify chat functionality works
- [ ] Test AI agent responses
- [ ] Check task creation and management
- [ ] Verify incident reporting
- [ ] Test attendance tracking
- [ ] Check permission requests
- [ ] Verify email notifications work
- [ ] Test Google OAuth integration

### 9. Performance & Security
- [ ] Run security scan with GitHub Actions
- [ ] Verify HTTPS is enforced on all services
- [ ] Check CORS settings are correct
- [ ] Test API rate limiting
- [ ] Verify environment variables are secure
- [ ] Check logs for any errors or warnings

### 10. Monitoring Setup
- [ ] Configure Render service monitoring
- [ ] Set up Vercel Analytics (optional)
- [ ] Configure uptime monitoring (UptimeRobot)
- [ ] Set up error tracking (Sentry - optional)
- [ ] Configure alert notifications

## CI/CD Pipeline

### 11. GitHub Actions
- [ ] Verify `.github/workflows/deploy.yml` is working
- [ ] Test that pushes to main trigger deployments
- [ ] Check that tests run before deployment
- [ ] Verify security scanning is enabled
- [ ] Test rollback procedures

## Domain & DNS (Optional)

### 12. Custom Domain Setup
- [ ] Configure custom domain on Vercel (frontend)
- [ ] Configure custom domain on Render (backend/agent)
- [ ] Set up DNS records
- [ ] Verify SSL certificates are installed
- [ ] Update environment variables with new URLs

## Documentation & Maintenance

### 13. Final Steps
- [ ] Update README with production URLs
- [ ] Document any manual deployment steps
- [ ] Create backup/restore procedures
- [ ] Set up regular maintenance schedule
- [ ] Train team on production monitoring
- [ ] Create incident response plan

## Production URLs
```
Frontend:  https://workhub.vercel.app
Backend:   https://workhub-backend.onrender.com  
AI Agent:  https://workhub-agent.onrender.com
Database:  Neon PostgreSQL (cloud)
Redis:     Upstash Redis (cloud)
```

## Emergency Contacts & Resources
- **Render Support**: https://render.com/docs
- **Vercel Support**: https://vercel.com/support
- **Neon Support**: https://neon.tech/docs
- **Upstash Support**: https://docs.upstash.com/

## Success Criteria ✅
- [ ] All services are accessible and healthy
- [ ] Users can register, login, and use all features
- [ ] AI agent responds to worker messages correctly
- [ ] Real-time chat and notifications work
- [ ] Email notifications are delivered
- [ ] Performance is acceptable (< 2s page loads)
- [ ] No critical errors in logs
- [ ] Auto-deployment pipeline is functional

---

**Deployment Status**: 🟡 Ready for Deployment
**Next Action**: Begin with database setup and backend deployment