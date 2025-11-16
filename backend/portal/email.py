import resend

def send_app_mail(subject, html, to):
    return resend.Emails.send({
        "from": "SafeIMEI <onboarding@resend.dev>",
        "to": [to],
        "subject": subject,
        "html": html,
    })
