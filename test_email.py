#!/usr/bin/env python3
"""
Email Test Script for WorkHub
This script will test if your email configuration is working properly.
"""
import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

async def test_email_connection():
    """Test email connection and send a test email"""
    
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    email_username = "shanmukhsiva54@gmail.com"  # Replace with your email
    email_password = "your-16-character-app-password"  # Replace with your app password
    from_email = email_username
    from_name = "WorkHub Test"
    to_email = email_username  # Send test email to yourself
    
    print("🧪 Testing WorkHub Email Configuration...")
    print(f"📧 SMTP Server: {smtp_server}:{smtp_port}")
    print(f"📨 From: {from_name} <{from_email}>")
    print(f"📬 To: {to_email}")
    print("-" * 50)
    
    try:
        # Create test message
        message = MIMEMultipart("alternative")
        message["Subject"] = "🧪 WorkHub Email Test - Success!"
        message["From"] = f"{from_name} <{from_email}>"
        message["To"] = to_email
        
        # HTML content
        html_content = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; text-align: center;">🎉 Email Test Successful!</h2>
                
                <p>Congratulations! Your WorkHub email configuration is working correctly.</p>
                
                <div style="background: #f0fdf4; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #22c55e;">
                    <h3 style="margin: 0 0 15px 0; color: #16a34a;">✅ Email Service Status:</h3>
                    <p><strong>SMTP Server:</strong> smtp.gmail.com:587</p>
                    <p><strong>Authentication:</strong> Successful</p>
                    <p><strong>TLS Encryption:</strong> Enabled</p>
                    <p><strong>Test Time:</strong> """ + str(__import__('datetime').datetime.now()) + """</p>
                </div>
                
                <p>Your WorkHub platform can now send:</p>
                <ul>
                    <li>📝 Employee registration emails</li>
                    <li>🚨 Incident alert notifications</li>
                    <li>📋 Task assignment emails</li>
                </ul>
                
                <p>You're ready to go! 🚀</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280; text-align: center;">
                    This is a test email from WorkHub Email Service
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = """
        🎉 Email Test Successful!
        
        Congratulations! Your WorkHub email configuration is working correctly.
        
        ✅ Email Service Status:
        - SMTP Server: smtp.gmail.com:587
        - Authentication: Successful  
        - TLS Encryption: Enabled
        
        Your WorkHub platform can now send:
        - Employee registration emails
        - Incident alert notifications  
        - Task assignment emails
        
        You're ready to go! 🚀
        
        - WorkHub Email Service
        """
        
        # Add both text and HTML parts
        text_part = MIMEText(text_content, "plain")
        html_part = MIMEText(html_content, "html")
        message.attach(text_part)
        message.attach(html_part)
        
        print("📡 Connecting to Gmail SMTP server...")
        
        # Send email using aiosmtplib
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=email_username,
            password=email_password,
        )
        
        print("✅ SUCCESS! Test email sent successfully!")
        print(f"📬 Check your inbox at {to_email}")
        print("🎉 Your WorkHub email system is ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED! Email test error: {e}")
        print("\n🔧 Troubleshooting Tips:")
        print("1. Make sure you're using a Gmail App Password (not regular password)")
        print("2. Verify 2-Factor Authentication is enabled on your Gmail account") 
        print("3. Check that the app password is 16 characters without spaces")
        print("4. Ensure your Gmail account allows 'Less secure app access'")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 WORKHUB EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    result = asyncio.run(test_email_connection())
    
    if result:
        print("\n" + "=" * 60)
        print("🎊 EMAIL SYSTEM READY FOR WORKHUB!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("⚠️  EMAIL CONFIGURATION NEEDS FIXING")
        print("=" * 60)