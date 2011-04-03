from email.mime.text import MIMEText

def create_msg(sender, subject, content):
    msg = MIMEText(content)
    msg['From'] = sender
    msg['Subject'] = subject
    return msg
