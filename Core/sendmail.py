# -*- coding: UTF-8 -*-
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
import os

server = "smtp.intel.com"
# fro = "yuanfangx.ma@intel.com"
# to = ["yuanfangx.ma@intel.com"]
# subject = "stress test report"


def get_text(htmlpath):
    with open(htmlpath, "r") as f:
        text = f.read()
    return text


def send_mail(htmlpath, fro, to, subject, files=[]):
    msg = MIMEMultipart()
    msg['From'] = fro
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    body = get_text(os.path.join(htmlpath, "result.html"))
    msg.attach(MIMEText(body, 'html'))
    for f in files:
        att = MIMEText(open(f, 'rb').read(), 'base64', 'gb2312')
        att["Content-Type"] = 'application/octet-stream'
        att.add_header("Content-Disposition", "attachment", filename=os.path.basename(f))
        msg.attach(att)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string())
    smtp.close()
