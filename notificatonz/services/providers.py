"""
Communication Service Providers
Free tier integrations for SMS and Email
"""

import os
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseCommunicationService(ABC):
    """Base class for all communication services"""
    
    @abstractmethod
    def send(self, recipient, subject, body):
        """Send a message"""
        pass
    
    def validate_recipient(self, recipient):
        """Validate recipient format"""
        return bool(recipient)


class EmailService(BaseCommunicationService):
    """Email service using Resend API (free tier available)"""
    
    def __init__(self):
        self.api_key = os.environ.get('RESEND_API_KEY', 're_2JNX4NBZ_2MPn3hn5EVpRZYeTufvvRh7H')
    
    def send(self, recipient, subject, body):
        """Send email using Resend API"""
        try:
            import resend
            resend.api_key = self.api_key
            
            r = resend.Emails.send({
                "from": "onboarding@resend.dev",
                "to": recipient,
                "subject": subject or "No Subject",
                "html": f"<p>{body.replace(chr(10), '<br>')}</p>"
            })
            logger.info(f"Email sent to {recipient} via Resend")
            return {'status': 'success', 'provider': 'resend', 'id': r.get('id')}
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {'status': 'failed', 'error': str(e)}


class SMSService(BaseCommunicationService):
    """SMS service - Free tier using Twilio trial or mock"""
    
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    def send(self, recipient, subject, body):
        """Send SMS"""
        if not self.account_sid or not self.auth_token:
            # Free tier: Log to console (simulated)
            logger.info(f"[SIMULATED SMS] To: {recipient}, Message: {body}")
            return {'status': 'success', 'provider': 'simulated', 'message': 'SMS simulated (configure Twilio for real sending)'}
        
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=body,
                from_=self.from_number,
                to=recipient
            )
            logger.info(f"SMS sent to {recipient}, SID: {message.sid}")
            return {'status': 'success', 'provider': 'twilio', 'sid': message.sid}
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return {'status': 'failed', 'error': str(e)}


class WhatsAppService(BaseCommunicationService):
    """WhatsApp service using Twilio (free tier available)"""
    
    def __init__(self):
        self.account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.from_number = 'whatsapp:' + os.environ.get('TWILIO_PHONE_NUMBER', '')
    
    def send(self, recipient, subject, body):
        """Send WhatsApp message"""
        if not self.account_sid or not self.auth_token:
            logger.info(f"[SIMULATED WHATSAPP] To: {recipient}, Message: {body}")
            return {'status': 'success', 'provider': 'simulated', 'message': 'WhatsApp simulated'}
        
        try:
            from twilio.rest import Client
            client = Client(self.account_sid, self.auth_token)
            message = client.messages.create(
                body=body,
                from_=self.from_number,
                to=f'whatsapp:{recipient}'
            )
            logger.info(f"WhatsApp sent to {recipient}")
            return {'status': 'success', 'provider': 'twilio', 'sid': message.sid}
        except Exception as e:
            logger.error(f"WhatsApp sending failed: {e}")
            return {'status': 'failed', 'error': str(e)}


def get_service(channel):
    """Factory function to get the appropriate service"""
    services = {
        'EMAIL': EmailService,
        'SMS': SMSService,
        'WHATSAPP': WhatsAppService,
    }
    service_class = services.get(channel.upper())
    if service_class:
        return service_class()
    raise ValueError(f"Unknown channel: {channel}")


def send_message(channel, recipient, subject, body):
    """Send a message through the appropriate service"""
    service = get_service(channel)
    return service.send(recipient, subject, body)