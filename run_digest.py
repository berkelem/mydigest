import goodreads
import sendemail

gdr_reader = goodreads.Goodreads(1)
email = sendemail.DigestEmail()

reviews = gdr_reader.get_reviews()
html_message = """"""
for review in reviews:
    html_message += gdr_reader.create_html_message(review) + """\n"""

email.yag_send(html_message)
