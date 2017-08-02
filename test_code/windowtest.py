from appJar import gui

app=gui()

app.startTabbedFrame("TabbedFrame")
app.startTab("Tab1")
app.addLabel("l1", "Tab 1 Label")
app.stopTab()

app.startTab("Tab2")
app.addLabel("l2", "Tab 2 Label")
app.stopTab()

app.startTab("Tab3")
app.addLabel("l3", "Tab 3 Label")
app.stopTab()
app.stopTabbedFrame()

app.go()








### import the library
##from appJar import gui
##import time
##
### handle button events
##def press(button):
##    if button == "Cancel":
##        app.stop()
##    else:
##        usr = app.getEntry("Username")
##        pwd = app.getEntry("Password")
##        print("User:", usr, "Pass:", pwd)
##
##
##
### create a GUI variable called app
##app = gui("Protobot Control Center", "700x500")
##
##app.showSplash("NASA Protobot Initiative", fill='blue', stripe='black', fg='white', font=44)
###time.sleep(3)
##
##app.setBg("grey")
##app.setFont(18)
##
### add & configure widgets - widgets get a name, to help referencing them later
##app.addLabel("banner", "Welcome to the Control Center")
##app.setLabelBg("banner", "blue")
##app.setLabelFg("banner", "white")
##app.setLabelSticky("banner", "nwe")
##
##
##
### link the buttons to the function called press
##app.addButtons(["refresh", "Cancel"], press)
##
### start the GUI
##app.go()
