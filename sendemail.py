import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import yagmail


class DigestEmail:

    def __init__(self):
        self.port = 465  # For SSL
        self.smtp_server = "smtp.gmail.com"
        self.sender_email = "mydigestbot@gmail.com"
        self.receiver_email = "berkelem@tcd.ie"
        self.yag = yagmail.SMTP(self.sender_email)

    def create_message(self, plaintext, htmltext):

        message = MIMEMultipart("alternative")
        message["Subject"] = "multipart test"
        message["From"] = self.sender_email
        message["To"] = self.receiver_email

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(plaintext, "plain")
        part2 = MIMEText(htmltext, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)
        return message

    def compile_html_text(self, html_elements):
        html = """<html>
                    <head>
                      <link rel="stylesheet" href="tweetstyle.css">
                    </head>
                    <body>
                      {}
                    </body>
                  </html>
                  """.format(html_elements)
        return html

    def send_email(self, message):
        password = input("Type your password and press enter: ")

        # Create a secure SSL context
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender_email, password)
            server.sendmail(self.sender_email, self.receiver_email, message.as_string())

    def yag_send(self, message):
        self.yag.send(
            to=self.receiver_email,
            subject="Daily review",
            contents=message
        )
