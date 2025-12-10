# Security Setup Guide

## Overview
This guide explains how to securely manage sensitive credentials and API keys in the WorkHub application.

## 🔐 Environment Variables Security

### Problem Solved
- **Before**: API keys and credentials were hardcoded in `docker-compose.yml`
- **After**: All sensitive data moved to secure `.env.docker` file (gitignored)

## 📁 File Structure

```
├── .env.docker          # 🔒 SECURE - Contains actual secrets (gitignored)
├── .env.example         # 📋 Template for other developers
├── docker-compose.yml   # 🐳 References environment variables
└── .gitignore          # 🚫 Prevents secrets from being committed
```

## 🚀 Quick Setup

### For New Developers

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workhub-back
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env.docker
   ```

3. **Edit `.env.docker` with your actual credentials**
   ```bash
   nano .env.docker  # or use your preferred editor
   ```

4. **Start the application**
   ```bash
   sudo docker-compose --env-file .env.docker up -d
   ```

## 🔑 Required Environment Variables

### Database
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection URL

### AI Services
- `GROQ_API_KEY`: Your Groq AI API key

### Email Configuration
- `SMTP_SERVER`: Email server address
- `SMTP_PORT`: Email server port
- `EMAIL_USERNAME`: SMTP username
- `EMAIL_PASSWORD`: SMTP password
- `FROM_EMAIL`: Sender email address
- `FROM_NAME`: Sender display name

### Google OAuth
- `GOOGLE_CLIENT_ID`: Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret
- `GOOGLE_REDIRECT_URI`: OAuth redirect URI

### Security
- `SECRET_KEY`: JWT signing secret
- `NEXTAUTH_SECRET`: NextAuth.js secret
- `NEXTAUTH_URL`: Application URL

### Storage
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key

## 🔒 Security Best Practices

### ✅ DO
- Keep `.env.docker` file local and never commit it
- Use strong, unique passwords and API keys
- Rotate API keys regularly
- Use different credentials for different environments (dev/staging/prod)

### ❌ DON'T
- Never hardcode credentials in source code
- Don't share `.env.docker` file via chat/email
- Don't use weak or default passwords
- Don't commit sensitive files to Git

## 🚨 Emergency Response

If credentials are accidentally committed:

1. **Immediately rotate all exposed credentials**
2. **Remove from Git history**:
   ```bash
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env.docker' \
   --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (⚠️ Only if safe to do so)
4. **Notify team members**

## 🔄 Environment Management

### Development
```bash
sudo docker-compose --env-file .env.docker up -d
```

### Production
```bash
# Use production environment file
sudo docker-compose --env-file .env.production up -d
```

### Testing
```bash
# Use test environment file
sudo docker-compose --env-file .env.test up -d
```

## 📋 Verification Checklist

- [ ] `.env.docker` file created and populated
- [ ] All containers start successfully
- [ ] API endpoints respond correctly
- [ ] AI agent processes messages
- [ ] Database connections work
- [ ] Email functionality tested (if configured)
- [ ] OAuth authentication working (if configured)

## 🆘 Troubleshooting

### Missing Environment Variables
```bash
# Check for warnings when starting
sudo docker-compose --env-file .env.docker config
```

### Environment Not Loading
```bash
# Verify file exists and is readable
ls -la .env.docker
cat .env.docker | head -5  # Check first few lines
```

### Service Connection Issues
```bash
# Check container logs
sudo docker logs workhub-backend
sudo docker logs workhub-agent
```

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Verify all environment variables are set correctly
3. Check container logs for specific error messages
4. Contact the development team with error details

---

**Remember**: Security is everyone's responsibility! 🔐