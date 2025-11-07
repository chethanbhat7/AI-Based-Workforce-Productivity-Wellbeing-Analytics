"""
Email Service for Burnout Monitoring System
Processes queued email notifications from Firestore
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending burnout and overtime alerts to supervisors.
    
    Supports multiple email providers:
    - Gmail SMTP
    - SendGrid API
    - AWS SES
    - Custom SMTP
    """
    
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        # Company dedicated email address for sending alerts
        self.from_email = os.getenv('FROM_EMAIL', 'hr-wellbeing@yourcompany.com')
        self.from_name = os.getenv('FROM_NAME', 'HR Wellbeing Team')
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_body: HTML content of the email
            text_body: Plain text alternative (optional)
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.from_name} <{self.from_email}>'
            msg['To'] = to_email
            
            # Add text/plain part if provided
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_burnout_alert(
        self,
        supervisor_email: str,
        member_name: str,
        member_email: str,
        burnout_risk: float,
        wellbeing_score: float
    ) -> bool:
        """
        Send burnout threshold alert to supervisor.
        
        Args:
            supervisor_email: Supervisor's email address
            member_name: Name of the affected member
            member_email: Email of the affected member
            burnout_risk: Calculated burnout risk percentage
            wellbeing_score: Member's wellbeing score
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f"⚠️ Burnout Alert: {member_name} has exceeded 70% burnout threshold"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .alert-box {{ background: #fee; border-left: 4px solid #e74c3c; padding: 15px; margin: 20px 0; }}
                .metric {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric-label {{ color: #7f8c8d; font-size: 12px; text-transform: uppercase; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #e74c3c; }}
                .actions {{ background: #e8f5e9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .actions h3 {{ color: #27ae60; margin-top: 0; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                .company-info {{ margin-top: 15px; font-size: 11px; color: #95a5a6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Burnout Threshold Alert</h1>
                    <p>Employee Wellbeing Monitoring System</p>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <p><strong>Dear Supervisor,</strong></p>
                        <p>This is an automated alert from the HR Wellbeing Team. A member of your team has exceeded the burnout risk threshold of 70%.</p>
                    </div>
                    
                    <h2>Team Member Details</h2>
                    <div class="metric">
                        <div class="metric-label">Name</div>
                        <div style="font-weight: 600; font-size: 18px;">{member_name}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Email</div>
                        <div style="font-weight: 600; font-size: 18px;">{member_email}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Burnout Risk Level</div>
                        <div class="metric-value">{burnout_risk:.1f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Wellbeing Score</div>
                        <div style="font-weight: 600; font-size: 18px;">{wellbeing_score:.0f}/100</div>
                    </div>
                    
                    <div class="actions">
                        <h3>✅ Recommended Immediate Actions</h3>
                        <ul>
                            <li>Schedule a confidential one-on-one meeting with {member_name} <strong>within 24 hours</strong></li>
                            <li>Review their current workload and task assignments</li>
                            <li>Consider redistributing tasks to other team members</li>
                            <li>Encourage taking time off or flexible working hours</li>
                            <li>Provide access to employee wellbeing resources and mental health support</li>
                            <li>Follow up regularly to monitor their wellbeing and progress</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p><strong>About This Alert</strong></p>
                        <p>This automated alert is sent when a team member's burnout risk exceeds 70%.</p>
                        <p>The wellbeing analytics system monitors employee health indicators daily and tracks weekly patterns.</p>
                        <div class="company-info">
                            <p>This email was sent from an automated system. Please do not reply directly.</p>
                            <p>For questions or support, contact your HR Wellbeing Team.</p>
                            <p>&copy; 2025 Workforce Wellbeing Analytics System | Employee Health & Wellness Program</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        BURNOUT THRESHOLD ALERT
        
        Member: {member_name} ({member_email})
        Burnout Risk: {burnout_risk:.1f}%
        Wellbeing Score: {wellbeing_score:.0f}/100
        
        RECOMMENDED ACTIONS:
        - Schedule a meeting with {member_name}
        - Review their workload
        - Consider redistributing tasks
        - Encourage time off
        - Provide wellbeing resources
        
        This alert is sent when burnout risk exceeds 70%.
        """
        
        return self.send_email(supervisor_email, subject, html_body, text_body)
    
    def send_overtime_alert(
        self,
        supervisor_email: str,
        member_name: str,
        member_email: str,
        overtime_count: int,
        week_start: str,
        week_end: str
    ) -> bool:
        """
        Send overtime alert to supervisor.
        
        Args:
            supervisor_email: Supervisor's email address
            member_name: Name of the affected member
            member_email: Email of the affected member
            overtime_count: Number of overtime occurrences this week
            week_start: Week start date (YYYY-MM-DD)
            week_end: Week end date (YYYY-MM-DD)
            
        Returns:
            bool: True if email sent successfully
        """
        subject = f"⏰ Overtime Alert: {member_name} has worked overtime {overtime_count} times this week"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%); 
                           color: white; padding: 30px; text-align: center; border-radius: 5px 5px 0 0; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 5px 0 0 0; font-size: 14px; opacity: 0.9; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
                .alert-box {{ background: #fff3cd; border-left: 4px solid #f39c12; padding: 15px; margin: 20px 0; }}
                .metric {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric-label {{ color: #7f8c8d; font-size: 12px; text-transform: uppercase; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #e67e22; }}
                .warning-box {{ background: #fee; padding: 20px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #e74c3c; }}
                .actions {{ background: #e8f5e9; padding: 20px; margin: 20px 0; border-radius: 5px; }}
                .actions h3 {{ color: #27ae60; margin-top: 0; }}
                .footer {{ text-align: center; color: #7f8c8d; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                .company-info {{ margin-top: 15px; font-size: 11px; color: #95a5a6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Excessive Overtime Alert</h1>
                    <p>Employee Wellbeing Monitoring System</p>
                </div>
                <div class="content">
                    <div class="alert-box">
                        <p><strong>Dear Supervisor,</strong></p>
                        <p>This is an automated alert from the HR Wellbeing Team. A member of your team has worked overtime {overtime_count} times this week, exceeding our healthy work-life balance threshold.</p>
                    </div>
                    
                    <h2>Team Member Details</h2>
                    <div class="metric">
                        <div class="metric-label">Name</div>
                        <div style="font-weight: 600; font-size: 18px;">{member_name}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Email</div>
                        <div style="font-weight: 600; font-size: 18px;">{member_email}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Overtime Occurrences</div>
                        <div class="metric-value">{overtime_count} times</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Current Week</div>
                        <div style="font-weight: 600; font-size: 18px;">{week_start} to {week_end}</div>
                    </div>
                    
                    <div class="warning-box">
                        <h3>⚠️ Impact on Employee Wellbeing</h3>
                        <p>Research shows that working overtime 3+ times in a single week is a strong indicator of:</p>
                        <ul>
                            <li><strong>Excessive workload</strong> that needs immediate redistribution</li>
                            <li><strong>Poor work-life balance</strong> affecting physical and mental wellbeing</li>
                            <li><strong>Increased burnout risk</strong> leading to reduced productivity and engagement</li>
                            <li><strong>Potential health issues</strong> including stress, fatigue, and decreased job satisfaction</li>
                        </ul>
                    </div>
                    
                    <div class="actions">
                        <h3>✅ Recommended Immediate Actions</h3>
                        <ul>
                            <li>Schedule a meeting with {member_name} <strong>within 24 hours</strong> to discuss their workload</li>
                            <li>Identify high-priority tasks that can be delegated to other team members</li>
                            <li>Review and adjust project timelines and deadlines if necessary</li>
                            <li>Ensure they take proper breaks and utilize their time off</li>
                            <li>Monitor their wellbeing score and stress indicators closely</li>
                            <li>Consider additional resources or hiring if workload is consistently excessive</li>
                        </ul>
                    </div>
                    
                    <div class="footer">
                        <p><strong>About This Alert</strong></p>
                        <p>This automated alert is triggered when a team member works overtime 3 or more times in a single week.</p>
                        <p>Overtime is tracked from Monday to Sunday and resets weekly.</p>
                        <div class="company-info">
                            <p>This email was sent from an automated system. Please do not reply directly.</p>
                            <p>For questions or support, contact your HR Wellbeing Team.</p>
                            <p>&copy; 2025 Workforce Wellbeing Analytics System | Employee Health & Wellness Program</p>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        OVERTIME ALERT
        
        Member: {member_name} ({member_email})
        Overtime Count: {overtime_count} times
        Week: {week_start} to {week_end}
        
        WHY THIS MATTERS:
        - Excessive workload
        - Poor work-life balance
        - Increased burnout risk
        - Potential health issues
        
        RECOMMENDED ACTIONS:
        - Meet with {member_name} immediately
        - Review and redistribute workload
        - Check project timelines
        - Ensure proper breaks
        - Monitor wellbeing indicators
        
        This alert triggers at 3+ overtimes per week.
        """
        
        return self.send_email(supervisor_email, subject, html_body, text_body)


# Singleton instance
email_service = EmailService()
