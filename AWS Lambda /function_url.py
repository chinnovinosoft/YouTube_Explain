
# Command to create web hook string —>> head -c 32 /dev/urandom | base64



import os, smtplib, ssl, json
from email.message import EmailMessage

GMAIL_USER = os.environ['email']
GMAIL_APP_PASSWORD = os.environ['GMAIL_APP_PASSWORD']
EMAIL_TO = os.environ['EMAIL_RECIPIENT']

def lambda_handler(event, context):
    print("Lambda Function webhook_func has been triggered !!")

    raw_body = event.get('body', '')
    print("Raw body -->", raw_body)

    # Parse JSON payload from GitHub
    try:
        body = json.loads(raw_body)
    except Exception as e:
        print("Failed to parse JSON:", str(e))
        return {'statusCode': 400, 'body': 'Invalid JSON'}

    # Extract repo and pusher
    repo = body['repository']['full_name']
    pusher = body['pusher']['name']
    print(f"Repo: {repo}, Pusher: {pusher}")

    # Email content
    msg_text = f"GitHub Push Event\n\nRepository: {repo}\nPushed by: {pusher}"

    message = EmailMessage()
    message.set_content(msg_text)
    message['Subject'] = f"GitHub Push to {repo}"
    message['From'] = GMAIL_USER
    message['To'] = EMAIL_TO

    # Send email using Gmail SMTP
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(message)
        print("Email sent successfully")
        return {'statusCode': 200, 'body': 'Email sent'}
    except Exception as e:
        print("Failed to send email:", str(e))
        return {'statusCode': 500, 'body': 'Email failed'}
