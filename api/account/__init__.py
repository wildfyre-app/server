from threading import Thread

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def send_mail(template_part, subject, to, context):
    def run(template_part, subject, to, context):
        mail_plain = get_template('account/mail_%s.txt' % template_part).render(context)
        mail_html = get_template('account/mail_%s.html' % template_part).render(context)

        subject = "[WildFyre] %s" % subject

        msg = EmailMultiAlternatives(subject, mail_plain, "noreply@wildfyre.net", [to])
        msg.attach_alternative(mail_html, "text/html")
        msg.send()

    Thread(target=run, kwargs={
        'template_part': template_part,
        'subject': subject,
        'to': to,
        'context': context,
    }, daemon=False).start()
