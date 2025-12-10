# Vercel Frontend Configuration
# Use this when setting up the frontend service on Vercel

## Project Settings
- **Framework Preset**: Next.js
- **Build Command**: `npm run build`
- **Output Directory**: `.next`
- **Install Command**: `npm install`
- **Development Command**: `npm run dev`

## Environment Variables
```bash
NEXT_PUBLIC_API_URL=https://workhub-backend.onrender.com
NEXT_PUBLIC_WS_URL=wss://workhub-backend.onrender.com
```

## Build & Development Settings
- **Node.js Version**: 20.x
- **Package Manager**: npm
- **Root Directory**: `frontend`

## Domain Configuration
- **Production Domain**: `workhub.vercel.app` (or custom domain)
- **Preview Deployments**: Enabled for pull requests
- **Custom Domain**: Add your domain if you have one

## Performance Optimization
- ✅ Enable Vercel Analytics
- ✅ Enable Vercel Speed Insights
- ✅ Image Optimization (built-in)
- ✅ Font Optimization (built-in)

## Git Integration
- ✅ Automatic deployments from Git
- ✅ Deploy on every push to main branch
- ✅ Preview deployments for pull requests

## Functions Configuration (if needed)
- **Region**: Washington, D.C., USA (us-east-1) or closest to backend
- **Memory**: 1024 MB
- **Timeout**: 10s

## Custom Domain Setup (Optional)
1. Add domain in Vercel dashboard
2. Configure DNS records:
   - Type: CNAME
   - Name: www (or @)
   - Value: cname.vercel-dns.com

## Security Headers
Vercel automatically includes security headers:
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy