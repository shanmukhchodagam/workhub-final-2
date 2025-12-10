# 📧 Fix WorkHub Email - Step by Step Guide

## 🔍 **Issue Identified**
Your email isn't working because you're using your regular Gmail password instead of a Gmail App Password.

---

## 📋 **Complete Email Setup Checklist**

### **Step 1: Generate Gmail App Password** ⭐ **MOST IMPORTANT**

1. **Go to Gmail Account Settings:**
   - Open: https://myaccount.google.com/security
   - Make sure 2-Step Verification is ON

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select App: "Mail"
   - Select Device: "Other" → Type "WorkHub"
   - Click "Generate"
   - **Copy the 16-character password** (example: `abcd efgh ijkl mnop`)

### **Step 2: Update Docker Configuration**

**Current (WRONG):**
```yaml
- EMAIL_PASSWORD=windows123bluebird  # ❌ Regular password won't work
```

**Should be (CORRECT):**
```yaml
- EMAIL_PASSWORD=abcd-efgh-ijkl-mnop  # ✅ 16-character app password
```

**Update your docker-compose.yml:**
```yaml
environment:
  # ... other variables ...
  - EMAIL_USERNAME=shanmukhsiva54@gmail.com
  - EMAIL_PASSWORD=PUT-YOUR-16-CHAR-APP-PASSWORD-HERE  # 🔑 Replace this!
  - FROM_EMAIL=shanmukhsiva54@gmail.com
  - FROM_NAME=WorkHub Team
```

### **Step 3: Test Email Before Starting Containers**

1. **Update the test script with your app password:**
   ```bash
   nano /media/chodagam-shanmukh/volume\ A/workhub/workhub/test_email.py
   ```

2. **Replace this line in test_email.py:**
   ```python
   email_password = "your-16-character-app-password"  # PUT YOUR APP PASSWORD HERE
   ```

3. **Run email test:**
   ```bash
   cd /media/chodagam-shanmukh/volume\ A/workhub/workhub
   python3 test_email.py
   ```

### **Step 4: Start WorkHub with Correct Configuration**

```bash
cd /media/chodagam-shanmukh/volume\ A/workhub/workhub
sudo docker-compose down
sudo docker-compose up -d
```

### **Step 5: Test Email in WorkHub**

1. **Login as Manager** at http://localhost:3000
2. **Register a New Employee** (email + name only)
3. **Check your email** for the welcome message
4. **Report an Incident** as employee to test alert emails

---

## 🚨 **Common Email Issues & Solutions**

### **Issue 1: "Authentication Failed"**
- ✅ **Solution:** You're using regular password instead of App Password
- 🔧 **Fix:** Generate Gmail App Password and update docker-compose.yml

### **Issue 2: "Connection Refused"** 
- ✅ **Solution:** Wrong SMTP server or port
- 🔧 **Fix:** Use `smtp.gmail.com:587`

### **Issue 3: "Less Secure Apps"**
- ✅ **Solution:** Gmail blocked third-party apps
- 🔧 **Fix:** Use App Passwords (more secure than allowing less secure apps)

### **Issue 4: "No Email Received"**
- ✅ **Check spam/junk folder**
- ✅ **Verify email address spelling**
- ✅ **Check container logs:** `sudo docker logs workhub-backend`

---

## 🧪 **Quick Email Test Commands**

```bash
# Test email configuration
cd /media/chodagam-shanmukh/volume\ A/workhub/workhub
python3 test_email.py

# Check backend email logs
sudo docker logs workhub-backend | grep -i email

# Test API endpoint
curl -X GET "http://localhost:8000/auth/me" -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📧 **Example Working Configuration**

```yaml
# docker-compose.yml
environment:
  - SMTP_SERVER=smtp.gmail.com
  - SMTP_PORT=587
  - EMAIL_USERNAME=shanmukhsiva54@gmail.com
  - EMAIL_PASSWORD=abcd-efgh-ijkl-mnop  # 16-char App Password
  - FROM_EMAIL=shanmukhsiva54@gmail.com
  - FROM_NAME=WorkHub Team
```

---

## 🎯 **Next Steps**

1. ⭐ **Generate Gmail App Password** (most critical step)
2. 🔧 **Update docker-compose.yml** with the app password  
3. 🧪 **Run test_email.py** to verify configuration
4. 🚀 **Restart WorkHub containers**
5. 📧 **Test employee registration** to see welcome emails

---

## ⚠️ **Security Notes**

- ✅ **App Passwords are MORE secure** than allowing "less secure apps"
- ✅ **Never share your app password** in public repositories
- ✅ **Use environment variables** for production deployments
- ✅ **App passwords only work with 2FA enabled**

---

**🎉 Once you follow these steps, WorkHub emails will work perfectly!**