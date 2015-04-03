#!usr/bin/python

# Imports
from socket import *
import ssl
import base64
from Tkinter import *
from tkFileDialog import askopenfilename
import os

codedImage = None

def send():
    # For attaching an image through telnet, we placed the setup commands for mime in a seperate files
    mimeSetup = open('mimeSetup.txt', 'r').read()
    mimeText = open('mimeText.txt', 'r').read()
    mimeImage = open('mimeImage.txt', 'r').read()

    mailFromName = frName.get() # Sending address taken from the GUI
    mailFromPass = frPass.get() # Sending password taken from the GUI
    mailTo = to.get() # Receiving address taken from the GUI for RCPT command
    rcptCC = cc.get() # CC address taken from the GUI for RCPT command
    mailCC = "cc: " + cc.get() + '\r\n' ## CC address for header content
    mailSubject = "Subject: " + subject.get() + '\r\n'  # Subject for the mail taken from the GUI.
    dataMailTo = "To: " + mailTo + '\r\n' # header message for header content
    message = msg.get() # Message taken from the GUI

    # GUI work, once a user clicks send the fields all get reset
    frName.delete(0, END)
    frPass.delete(0, END)
    to.delete(0, END)
    cc.delete(0, END)
    msg.delete(0, END)
    subject.delete(0, END)

    endmsg = "\r\n.\r\n" # Used for ending the DATA command (sending of a mail)

    # Choose a mail server (ex: google mail server) and call it mailserver
    # Create socket called clientSocket and establish a TCP connection with mail Server
    mailServer = "smtp.gmail.com" # Mail server
    clientSocket = socket(AF_INET, SOCK_STREAM) # Establishing socket
    clientSocket.connect((mailServer, 587)) # Socket connections to the mail server
    recv = clientSocket.recv(1024) # response message
    print '\r\n' + "Mail server: " + mailServer 
    print recv # Prints response message to the terminal
    if recv[:3]!= "220":  # Checks status code of the response                                          
        print "220 reply not received from server."  # Response did not contain the proper status code

    # Send HELO command and print server response
    heloCommand = 'HELO PEOPLE\r\n'
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024)
    print "Client: HELO PEOPLE"
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not recevied from server'

    # Send TLS command, which is used for authentication (in our case, authenticates a gmail user)
    tlsCommand = 'STARTTLS\r\n'
    clientSocket.send(tlsCommand)
    tls = clientSocket.recv(1024)
    print "Client: STARTTLS"
    print "Server: " + tls
    if tls[:3] != '220':
        print 'not able to start tls'

    # wrap socket, after tls begins, we need to wrap the clientSocket into an SSL socket. This grants secruity in the following sockets
    clientSocketSSL = ssl.wrap_socket(clientSocket)

    # Send HELO command with the SSL socket and print server response
    heloCommand = 'HELO PEOPLE\r\n'
    clientSocketSSL.send(heloCommand)
    recv1 = clientSocketSSL.recv(1024)
    print "Client HELO PEOPLE"
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not recevied from server'

    # Authentication 
    authCommand = 'AUTH LOGIN\r\n'
    clientSocketSSL.send(authCommand)
    auth = clientSocketSSL.recv(1024)
    print "Client: AUTH LOGIN"
    print "Server: " + auth
    if auth[:3] != '334':
        print 'Not able to do Authentication'

    # Send encrypted user name
    encodedName =  base64.b64encode(mailFromName);
    clientSocketSSL.send(encodedName + "\r\n")
    user = clientSocketSSL.recv(1024)
    print "Server: " + user
    print "Client: encoded username"

    # Send encrypted password
    encodedPass =  base64.b64encode(mailFromPass);
    clientSocketSSL.send(encodedPass + "\r\n")
    password = clientSocketSSL.recv(1024)
    print "Server: " +  password
    print "Client: encoded password" + '\r\n'
        
    # Send MAIL FROM command and print server response
    clientSocketSSL.send("MAIL FROM: <" + mailFromName + "> \r\n")
    recv1 = clientSocketSSL.recv(1024)
    print "Client: MAIL FROM " + mailFromName
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not received from server'

    # Send RCPT TO command and print server response, this RCPT issues to the "To: " sender in the header
    clientSocketSSL.send("RCPT TO: <" + mailTo + "> \r\n")
    recv1 = clientSocketSSL.recv(1024)
    print "Client: RCPT TO " + mailTo
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not received from server'

    # SEND RCPT TO command for the CC email address
    clientSocketSSL.send("RCPT TO: <" + rcptCC + "> \r\n")
    recv1 = clientSocketSSL.recv(1024)
    print "Client: RCPT TO " + rcptCC
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not received from server'

    # Send DATA command and print server response
    clientSocketSSL.send('DATA\r\n')
    recv1 = clientSocketSSL.recv(1024)
    print "Client: DATA"
    print "Server: " + recv1
    if recv1[:3] != '354':
        print '250 reply not received from server'

    # Send message data
    clientSocketSSL.send(mailCC) ## CC field
    print "CC: " + rcptCC
    clientSocketSSL.send(dataMailTo) # Sends To field
    print "To: " + mailTo
    clientSocketSSL.send(mailSubject) # Sends subject field
    print "Subject: " + mailSubject + '\r\n'
    clientSocketSSL.send(mimeSetup + '\r\n' + '\r\n') # inital mime setup
    print mimeSetup + '\r\n' + '\r\n'
    clientSocketSSL.send(mimeText + '\r\n' + '\r\n') # mime setup for sending text
    print mimeText + '\r\n' + '\r\n'
    clientSocketSSL.send(message + '\r\n' + '\r\n')  # sends message
    print message + '\r\n' + '\r\n'

    if (codedImage != None): # Checks to make sure an image is being sent, (may throw a warning if file attacher was opened and nothing was selected)
        clientSocketSSL.send(mimeImage + '\r\n' + '\r\n') # mime setup for image
        print mimeImage + '\r\n' + '\r\n'
        clientSocketSSL.send(base64.b64encode(codedImage) + '\r\n' + '\r\n') # encodes and sends image
        print "encoded image here"
        clientSocketSSL.send("--mimeEmail--") # end of mime 

    # Message ending, needs to end with a single period
    clientSocketSSL.send(endmsg)
    recv1 = clientSocketSSL.recv(1024)
    print endmsg
    print "Server: " + recv1
    if recv1[:3] != '250':
        print '250 reply not received from server'

    # Send QUIT command and get server response
    clientSocketSSL.send('QUIT\r\n')
    print "Client: QUIT"
    clientSocketSSL.close()

# Function that returns selected JPEG image from the file chooser
def findFile():
    global codedImage
    with open(askopenfilename(), "rb") as image_file:
        codedImage = image_file.read()
        
# GUI display
root = Tk()
root.resizable(width=FALSE, height=FALSE)
root.wm_title("Mail Client")
frNameLabel = Label(root, text="FROM EMAIL:", width=15).grid(row=0, column=0)
frName = Entry(root, width=50)
frName.grid(row=0, column=1)
frPassLabel = Label(root, text="FROM PASSWORD:", width=15).grid(row=1, column=0)
frPass = Entry(root, show='*', width=50)
frPass.grid(row=1, column=1)
toLabel = Label(root, text="TO:", width=15).grid(row=2, column=0)
to = Entry(root, width=50)
to.grid(row=2, column=1)
ccLabel = Label(root, text="CC:", width=15).grid(row=3, column=0)
cc = Entry(root, width=50)
cc.grid(row=3, column=1)
subjectLabel = Label(root, text="SUBJECT:", width=15).grid(row=4, column=0)
subject = Entry(root, width=50)
subject.grid(row=4, column=1)
msgLabel = Label(root, text="MESSAGE:", width=15).grid(row=5, column=0)
msg = Entry(root, width=50)
msg.grid(row=5, column=1, ipady=30)
buttonAttach = Button(root, text='ATTACH IMAGE', width=50, command=findFile)
buttonAttach.grid(row=6, column=0)
button = Button(root, text='Send', width=50, command=send)
button.grid(row=6, column=1)
mainloop()