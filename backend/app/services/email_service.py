"""
Email service configuration and utilities
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import asyncio
import aiosmtplib
from jinja2 import Environment, BaseLoader
import os
from app.core.config import settings

class EmailService:
    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.email_username)
        self.from_name = os.getenv("FROM_NAME", "WorkHub Team")
        
        print(f"📧 Email service configured:")
        print(f"   Server: {self.smtp_server}:{self.smtp_port}")
        print(f"   From: {self.from_name} <{self.from_email}>")
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """Send an email asynchronously"""
        try:
            if not self.email_username or not self.email_password:
                print("❌ Email credentials not configured!")
                return False
                
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            
            # Add text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)
                
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)
            
            # Send email using aiosmtplib
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.email_username,
                password=self.email_password,
            )
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False

    async def send_employee_registration_email(
        self,
        employee_email: str,
        employee_name: str,
        temp_password: str,
        manager_name: str
    ) -> bool:
        """Send registration email to new employee"""
        
        subject = f"Welcome to WorkHub - Your Account is Ready!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; text-align: center;">🎉 Welcome to WorkHub!</h2>
                
                <p>Hello <strong>{employee_name}</strong>,</p>
                
                <p>Great news! <strong>{manager_name}</strong> has created your WorkHub account. You can now access our field worker management platform.</p>
                
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin: 0 0 15px 0; color: #1f2937;">🔐 Your Login Credentials:</h3>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {employee_email}</p>
                    <p style="margin: 5px 0;"><strong>Temporary Password:</strong> <code style="background: #e5e7eb; padding: 2px 6px; border-radius: 4px;">{temp_password}</code></p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/login" 
                       style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        🚀 Login to WorkHub
                    </a>
                </div>
                
                <h3 style="color: #1f2937;">📱 What you can do with WorkHub:</h3>
                <ul style="padding-left: 20px;">
                    <li>💬 Chat with AI assistant for instant help</li>
                    <li>📋 View and update your assigned tasks</li>
                    <li>🚨 Report incidents and safety issues</li>
                    <li>⏰ Track your attendance and work hours</li>
                    <li>📞 Communicate directly with your manager</li>
                </ul>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b; margin: 20px 0;">
                    <p style="margin: 0;"><strong>🔒 Security Note:</strong> Please change your password after your first login for security.</p>
                </div>
                
                <p>If you have any questions or need assistance, don't hesitate to reach out to <strong>{manager_name}</strong> or use the AI chat assistant in the platform.</p>
                
                <p>Welcome to the team!</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280; text-align: center;">
                    This email was sent by WorkHub Field Worker Management System<br>
                    If you believe this email was sent in error, please contact your system administrator.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to WorkHub!
        
        Hello {employee_name},
        
        {manager_name} has created your WorkHub account.
        
        Your Login Credentials:
        Email: {employee_email}
        Temporary Password: {temp_password}
        
        Login at: http://localhost:3000/login
        
        Features available:
        - Chat with AI assistant
        - View and update tasks
        - Report incidents
        - Track attendance
        - Communicate with manager
        
        Please change your password after first login.
        
        Welcome to the team!
        
        - WorkHub Team
        """
        
        return await self.send_email(
            to_email=employee_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    async def send_incident_alert_email(
        self,
        manager_email: str,
        worker_name: str,
        incident_description: str,
        incident_time: str
    ) -> bool:
        """Send incident alert to manager"""
        
        subject = f"🚨 URGENT: Incident Reported by {worker_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: #fee2e2; border: 1px solid #fecaca; border-radius: 8px; padding: 20px; margin-bottom: 20px;">
                    <h2 style="color: #dc2626; margin: 0 0 10px 0;">🚨 Incident Alert</h2>
                    <p style="margin: 0; font-weight: bold; color: #7f1d1d;">Immediate attention required</p>
                </div>
                
                <h3 style="color: #1f2937;">📋 Incident Details:</h3>
                <div style="background: #f9fafb; padding: 15px; border-radius: 6px; border-left: 4px solid #ef4444;">
                    <p><strong>Reported by:</strong> {worker_name}</p>
                    <p><strong>Time:</strong> {incident_time}</p>
                    <p><strong>Description:</strong></p>
                    <p style="background: white; padding: 10px; border-radius: 4px; margin: 10px 0;">
                        {incident_description}
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/manager" 
                       style="background: #dc2626; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        🔍 View in Dashboard
                    </a>
                </div>
                
                <div style="background: #fef3c7; padding: 15px; border-radius: 6px; border-left: 4px solid #f59e0b;">
                    <p style="margin: 0;"><strong>⚡ Action Required:</strong> Please review this incident immediately and take appropriate action to ensure worker safety.</p>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280; text-align: center;">
                    This is an automated alert from WorkHub Safety System
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=manager_email,
            subject=subject,
            html_body=html_body
        )

    async def send_task_assignment_email(
        self,
        employee_email: str,
        employee_name: str,
        task_title: str,
        task_description: str,
        due_date: str,
        assigned_by: str
    ) -> bool:
        """Send task assignment notification"""
        
        subject = f"📋 New Task Assigned: {task_title}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; text-align: center;">📋 New Task Assignment</h2>
                
                <p>Hello <strong>{employee_name}</strong>,</p>
                
                <p>You have been assigned a new task by <strong>{assigned_by}</strong>.</p>
                
                <div style="background: #eff6ff; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #2563eb;">
                    <h3 style="margin: 0 0 15px 0; color: #1e40af;">📝 Task Details:</h3>
                    <p><strong>Title:</strong> {task_title}</p>
                    <p><strong>Due Date:</strong> {due_date}</p>
                    <p><strong>Description:</strong></p>
                    <div style="background: white; padding: 15px; border-radius: 6px; margin: 10px 0;">
                        {task_description}
                    </div>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:3000/worker" 
                       style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; font-weight: bold;">
                        📱 View Task in App
                    </a>
                </div>
                
                <p>Please review the task details and start working on it as scheduled. If you have any questions, feel free to reach out to <strong>{assigned_by}</strong> or use the chat feature in the app.</p>
                
                <p>Good luck with your task!</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                <p style="font-size: 12px; color: #6b7280; text-align: center;">
                    This notification was sent by WorkHub Task Management System
                </p>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=employee_email,
            subject=subject,
            html_body=html_body
        )

# Global email service instance
email_service = EmailService()