#!/usr/bin/env python
# -*- coding: ascii -*- 

# wingHotkeys.py
# Author:  Eric Pavey - warpcat@sbcglobal.net

#import wingapi
import wingapi
import socket
import os,time,locale
import codecs

#=============------------  2 unicode  ------------ =============#
def u(s, encoding):
	if isinstance(s, unicode):
		return s
	else:
		return unicode(s, encoding)
#=============------------  2 unicode  ------------ =============#

#=============------------  myself mod  ------------ =============#
def to_maya():
	"""auto to maya"""
	editor = wingapi.gApplication.GetActiveEditor()
	doc = editor.GetDocument()
	doctype = doc.GetMimeType()
	if 'text/x-python' in str(doctype):
		python_to_maya()
	else:
		mel_to_maya()
#=============------------  myself mod  ------------ =============#


def getWingText():
	"""
	Based on the Wing API, get the selected text, and return it
	"""
	editor = wingapi.gApplication.GetActiveEditor()
	if editor is None:
		return
	doc = editor.GetDocument()
	start, end = editor.GetSelection()
	txt = doc.GetCharRange(start, end)
	return txt

def send_to_maya(language):
	"""
	Send the selected code to be executed in Maya

	language : string : either 'mel' or 'python'
	"""
	# The commandPort you opened in userSetup.mel.  Make sure this matches!
	commandPort = 6000

	if language != "mel" and language != "python":
		raise ValueError("Expecting either 'mel' or 'python'")

	# Save the text to a temp file.  If we're dealing with mel, make sure it
	# ends with a semicolon, or Maya could become angered!
	txt = getWingText()
	if language == 'mel':
		if not txt.endswith(';'):
			txt += ';'
	tempFile = os.path.join(os.environ['TMP'], 'wingData.txt')

	txt_unicode = u(txt,'utf-8')
	f = open(tempFile, "w")
	txt_u8 = txt_unicode.encode('utf-8')
	f.write(txt_u8)

	f.close()

	# Create the socket that will connect to Maya,  Opening a socket can vary from
	# machine to machine, so if one way doesn't work, try another... :-S
	#mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#mSocket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # Works!
	# More generic code for socket creation thanks to Derek Crosby:

	#res = socket.getaddrinfo("127.0.0.1", commandPort, socket.AF_INET, socket.SOCK_STREAM)
	#af, socktype, proto, canonname, sa = res[0]

	#-----------------------debug-----------------------------
	#f=open('D:/Wing IDE 4 scripts/f.txt','w')
	#f.write(str(af)+' '+ str(socktype)+' '+str(proto))
	#f.close()
	#----------------------------------------------------


	#mSocket = socket.socket(af, socktype, proto)
	mSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Now ping Maya over the command-port
	try:
		# Make our socket-> Maya connection:   There are different connection ways
		# which vary between machines, so sometimes you need to try different
		# solutions to get it to work... :-S
		#mSocket.connect(("127.0.0.1", commandPort))
		#mSocket.connect(("::1",commandPort))  #works!
		mSocket.connect(("127.0.0.1", commandPort))
		
		#sendCode = 'python("import sys")' 
		#mSocket.send(sendCode)
		#sendCode = 'python("reload(sys)")' 
		#mSocket.send(sendCode)
		#sendCode = 'python("sys.setdefaultencoding(\'utf-8\')")'
		#mSocket.send(sendCode)
		
		# Send our code to Maya:
		sendCode = u'python("import executeWingCode; executeWingCode.main(\'%s\')")' %language
		mSocket.send(sendCode)
	except Exception, e:
		print "Send to Maya fail:", e
	time.sleep(0.3)
	mSocket.close()

def python_to_maya():
	"""Send the selected Python code to Maya"""
	send_to_maya('python')

def mel_to_maya():
	"""Send the selected code to Maya as mel"""
	send_to_maya('mel')

def test_script():
	app = wingapi.gApplication
	v = "Product info is: " + str(app.GetProductInfo())
	doc = app.GetCurrentFiles()
	dira = app.GetStartingDirectory()
	v += "\nAnd you typed: %s" % doc
	v += "\nAnd you typed: %s" % dira
	wingapi.gApplication.ShowMessageDialog("Test Message", v)

def open_folder():
	app = wingapi.gApplication
	folder = app.GetStartingDirectory()
	app.OpenURL(folder)