# Environment Variables Setup

## 🔐 Security Notice
This project uses environment variables to keep sensitive information secure. **Never commit `.env` or `.env.docker` files to Git.**

## 🚀 Quick Setup

1. **Copy the example file:**
   ```bash
   cp .env.example .env.docker
   ```

2. **Update the values in `.env.docker` with your actual credentials:**
   - Database URL (Neon, PostgreSQL, etc.)
   - Groq API Key for AI features
   - Email credentials for notifications
   - Google OAuth credentials
   - Other API keys and secrets

3. **Run the application:**
   ```bash
   docker-compose up -d
   ```

## 📋 Required Environment Variables

### Database
- `DATABASE_URL`: PostgreSQL connection string with asyncpg driver

### AI Services
- `GROQ_API_KEY`: API key for Groq LLM services

### Email Services  
- `EMAIL_USERNAME`: SMTP email username
- `EMAIL_PASSWORD`: SMTP email app password (not regular password)
- `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)

### Google OAuth
- `GOOGLE_CLIENT_ID`: OAuth 2.0 client ID
- `GOOGLE_CLIENT_SECRET`: OAuth 2.0 client secret

### Storage
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key

### Security
- `SECRET_KEY`: JWT signing secret (generate a strong random string)

## 🔧 Getting API Keys

### Groq API Key
1. Visit [Groq Console](https://console.groq.com)
2. Sign up/Login
3. Create an API key
4. Copy the key to `GROQ_API_KEY`

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Set redirect URI: `http://localhost:8000/auth/google/callback`

### Gmail App Password
1. Enable 2-factor authentication on Gmail
2. Generate an App Password
3. Use the 16-character password (not your regular Gmail password)

## ⚠️ Important Notes

- **Never share your `.env.docker` file**
- **Generate strong, unique secrets for production**
- **Use different credentials for development/staging/production**
- **Regularly rotate API keys and passwords**
- **Keep this file updated when adding new environment variables**