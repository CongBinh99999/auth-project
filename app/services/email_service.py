"""Email Service - Gửi email qua SMTP.

Service gửi các loại email:
- Verification email sau khi đăng ký
- Password reset email
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Annotated

from fastapi import Depends

from app.config.settings import get_settings

settings = get_settings()


class EmailService:
    """Service gửi email qua SMTP.
    
    Sử dụng SMTP để gửi các loại email:
    - Email xác thực tài khoản
    - Email reset mật khẩu
    
    Attributes:
        smtp_server: SMTP server address.
        smtp_port: SMTP server port.
        username: SMTP username (email).
        password: SMTP password (app password).
    """
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.timeout = settings.SMTP_TIMEOUT
    
    def _create_message(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str
    ) -> MIMEMultipart:
        """Tạo email message."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.username
        message["To"] = to_email
        
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        return message
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Gửi email qua SMTP.
        
        Args:
            to_email: Email người nhận.
            subject: Tiêu đề email.
            html_content: Nội dung HTML.
            
        Returns:
            True nếu gửi thành công.
        """
        if not self.username or not self.password:
            # Skip sending if SMTP not configured
            print(f"[EMAIL] SMTP not configured. Would send to: {to_email}")
            return False
        
        try:
            message = self._create_message(to_email, subject, html_content)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=self.timeout) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, to_email, message.as_string())
            
            print(f"[EMAIL] Sent successfully to: {to_email}")
            return True
            
        except (smtplib.SMTPException, OSError) as e:
            print(f"[EMAIL] Failed to send to {to_email}: {e!s}")
            return False
    
    def send_verification_email(self, to_email: str, token: str, base_url: str = "http://localhost:8000") -> bool:
        """Gửi email xác thực tài khoản.
        
        Args:
            to_email: Email người nhận.
            token: Verification token.
            base_url: Base URL của ứng dụng.
            
        Returns:
            True nếu gửi thành công.
        """
        verify_url = f"{base_url}/api/v1/auth/verify-email?token={token}"
        
        subject = "Xác thực tài khoản - AuthProject"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Xác thực Email</h1>
                </div>
                <div class="content">
                    <p>Xin chào,</p>
                    <p>Cảm ơn bạn đã đăng ký tài khoản. Vui lòng click vào nút bên dưới để xác thực email:</p>
                    <p style="text-align: center;">
                        <a href="{verify_url}" class="button">Xác thực Email</a>
                    </p>
                    <p>Hoặc copy link sau vào trình duyệt:</p>
                    <p style="word-break: break-all; background: #e5e7eb; padding: 10px; border-radius: 4px;">
                        {verify_url}
                    </p>
                    <p>Link này sẽ hết hạn sau {settings.EMAIL_VERIFICATION_EXPIRE_MINUTES} phút.</p>
                </div>
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)
    
    def send_password_reset_email(self, to_email: str, token: str, base_url: str = "http://localhost:8000") -> bool:
        """Gửi email reset mật khẩu.
        
        Args:
            to_email: Email người nhận.
            token: Reset token.
            base_url: Base URL của ứng dụng.
            
        Returns:
            True nếu gửi thành công.
        """
        reset_url = f"{base_url}/reset-password?token={token}"
        
        subject = "Đặt lại mật khẩu - AuthProject"
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #DC2626; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; background: #DC2626; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                .warning {{ background: #FEF3C7; border: 1px solid #F59E0B; padding: 10px; border-radius: 4px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Đặt lại mật khẩu</h1>
                </div>
                <div class="content">
                    <p>Xin chào,</p>
                    <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                    <p style="text-align: center;">
                        <a href="{reset_url}" class="button">Đặt lại mật khẩu</a>
                    </p>
                    <p>Hoặc copy link sau vào trình duyệt:</p>
                    <p style="word-break: break-all; background: #e5e7eb; padding: 10px; border-radius: 4px;">
                        {reset_url}
                    </p>
                    <div class="warning">
                        <strong>⚠️ Lưu ý:</strong> Link này sẽ hết hạn sau {settings.PASSWORD_RESET_EXPIRE_MINUTES} phút.
                        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                    </div>
                </div>
                <div class="footer">
                    <p>Email này được gửi tự động, vui lòng không reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(to_email, subject, html_content)


def get_email_service() -> EmailService:
    """Dependency injection factory cho EmailService."""
    return EmailService()


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
