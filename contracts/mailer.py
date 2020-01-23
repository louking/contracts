###########################################################################################
# mailer - send email
#
#   Date        Author          Reason
#   ----        ------          ------
#   11/02/18    Lou King        Create (adapted from https://docs.python.org/2/library/email-examples.html)
#
#   Copyright 2018 Lou King
#
###########################################################################################
'''
mailer - send email
================================================
'''
# standard
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode

# pypi
from flask import current_app
from googleapiclient.discovery import build
from apiclient import errors

debug = False

#----------------------------------------------------------------------
def sendmail(subject, fromaddr, toaddr, html, text='', ccaddr=None ):
#----------------------------------------------------------------------
    '''
    send mail

    :param subject: subject of email
    :param fromaddr: from address to use
    :param toaddr: to address to use, may be list of addresses
    :param html: html to send
    :param text: optional text alternative to send
    '''
    current_app.logger.info('sendmail(): from={}, to={}, cc={}, subject="{}"'.format(fromaddr, toaddr, ccaddr, subject))

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = fromaddr
    if not isinstance(toaddr, list):
        toaddr = [toaddr]
    msg['To'] = ', '.join(toaddr)
    if ccaddr:
        if not isinstance(ccaddr, list):
            ccaddr = [ccaddr]
        msg['Cc'] = ', '.join(ccaddr)

    # Record the MIME types of both parts - text/plain and text/html.
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    if text:
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
    part2 = MIMEText(html, 'html')
    msg.attach(part2)

    # # Send the message via SMTP server
    # s = smtplib.SMTP(smtphost)
    # # sendmail function takes 3 arguments: sender's address, recipient's address
    # # and message to send - here it is sent as one string.
    # s.sendmail(fromaddr, toaddr, msg.as_string())
    # s.quit()

    # get credentials using the service account file
    gmail = gmail_service_account_login( current_app.config['APP_SERVICE_ACCOUNT_FILE'], 'librarian@steeplechasers.org' )

    try:
        if debug: current_app.logger.debug('sendmail(): msg.as_string()={}'.format(msg.as_string()))
        message = { 'raw' : urlsafe_b64encode(msg.as_bytes()).decode("utf-8") }
        sent = gmail.users().messages().send(userId='me', body=message).execute()
        return sent
    except errors.HttpError as error:
        current_app.logger.error('sendmail(): An error occurred: {}'.format(error))
        raise

#----------------------------------------------------------------------
def gmail_service_account_login( service_account_file, delegated_user ):
#----------------------------------------------------------------------
    '''
    log into service account based on service account file
    '''
    # adapted from https://medium.com/lyfepedia/sending-emails-with-gmail-api-and-python-49474e32c81f

    from google.oauth2 import service_account

    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    credentials = service_account.Credentials.from_service_account_file(
          service_account_file, scopes=SCOPES)
    delegated_credentials = credentials.with_subject( delegated_user )
    service = build('gmail', 'v1', credentials=delegated_credentials)
    return service