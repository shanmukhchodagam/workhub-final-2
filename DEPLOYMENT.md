# Deployment Guide

## Vercel (Frontend)
1. Connect GitHub repo
2. Root Directory: `frontend`
3. Environment Variables:
   - NEXT_PUBLIC_API_URL: https://your-backend.onrender.com

## Render (Backend)
1. Connect GitHub repo  
2. Dockerfile Path: `backend/Dockerfile`
3. Environment Variables:
   - DATABASE_URL: [Your Neon URL]
   - GOOGLE_CLIENT_ID: [Your Google Client ID]
   - GOOGLE_CLIENT_SECRET: [Your Google Client Secret]
   - EMAIL_PASSWORD: [Your Gmail App Password]
   - FROM_EMAIL: shanmukhsiva54@gmail.com
   - FROM_NAME: WorkHub Team
   - GOOGLE_REDIRECT_URI: https://your-backend.onrender.com/auth/google/callback

## After Deployment
1. Update Google OAuth redirect URI in Google Console
2. Update NEXT_PUBLIC_API_URL in Vercel to your Render backend URL
3. Test the application

## URLs will be:
- Frontend: https://workhub-new.vercel.app
- Backend: https://workhub-new.onrender.com