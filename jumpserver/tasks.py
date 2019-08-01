# # -*- coding: utf-8 -*-
# from __future__ import absolute_import
#
# from celery import task
# from jumpserver.settings import *
# import icalendar
# from icalendar import vCalAddress, vText
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.header import Header
# import email
# import smtplib
# import time
# import sys
#
# reload(sys)
# sys.setdefaultencoding('utf8')
#
#
# @task
# def sendAppointment(start, end, meet, to_email, subj, description,
#                     users, status='confirmed', uid=str(time.time())):
#     try:
#         if not isinstance(subj, unicode):
#             subj = unicode(subj)
#         reminderHours = 1
#         sender = EMAIL_HOST_USER
#
#         cal = icalendar.Calendar()
#         cal.add('prodid', '-//My calendar product//mxm.dk//')
#         cal.add('version', '2.0')
#         cal.add('method', "REQUEST")
#
#         event = icalendar.Event()
#         event.add('status', status)
#         event.add('category', "Event")
#         event.add('summary', subj)
#         event.add('description', description)
#         event.add('location', meet)
#         event.add('dtstart', start)
#         event.add('dtend', end)
#         # Generate some unique ID
#         event['uid'] = uid
#         event.add('priority', 5)
#         event.add('sequence', 1)
#         # event.add('From', users.email)
#
#         organizer = vCalAddress(users.email)
#         organizer.params['cn'] = vText(users.name)
#         organizer.params['role'] = vText('CHAIR')
#         organizer.params['delegated-from'] = vCalAddress(users.email)
#         event['organizer'] = organizer
#
#         # attendee = vCalAddress('dengtingru@huli.com')
#         # attendee.params['cn'] = vText('邓廷儒')
#         # attendee.params['role'] = vText('REQ-PARTICIPANT')
#         # event.add('attendee', attendee, encode=0)
#
#         alarm = icalendar.Alarm()
#         alarm.add("action", "DISPLAY")
#         alarm.add('description', "Reminder")
#         # alarm.add("trigger", datetime.timedelta(hours=-reminderHours))
#         # The only way to convince Outlook to do it correctly
#         alarm.add("TRIGGER;RELATED=START", "-PT{0}H".format(reminderHours))
#
#         event.add_component(alarm)
#         cal.add_component(event)
#
#         msg = MIMEMultipart("alternative")
#         msg["Subject"] = subj
#         msg["Content-class"] = "urn:content-classes:calendarmessage"
#         msg['From'] = Header(users.email, 'utf-8')
#         msg.attach(MIMEText(description, 'html', 'utf-8'))
#         msg["Accept-Language"] = "zh-CN"
#         msg["Accept-Charset"] = "ISO-8859-1,utf-8"
#
#         # filename = "invite.ics"
#
#         part = email.MIMEBase.MIMEBase('text', "calendar", method="REQUEST")
#         part.set_payload(cal.to_ical())
#
#         email.Encoders.encode_base64(part)
#
#         msg.attach(part)
#
#         s = smtplib.SMTP()
#         s.connect(EMAIL_HOST)
#         s.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
#
#         s.sendmail(sender, to_email, msg.as_string())
#
#         s.quit()
#     except Exception, e:
#         print e
