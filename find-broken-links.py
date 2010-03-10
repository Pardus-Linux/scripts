#!/usr/bin/python
# -*- coding: utf-8 -*-

# This is a VirtualBox integrated test platform
# in order to find broken links of an installed package.

import  os, sys, time, getpass, pxssh

try:
    import pexpect
except:
    print "you need to install pexpect module"
    exit()

class FindBrokenLinks:
    def __init__(self):

        self.revdepOutput = ""

        self.revdep_outfile = open("revdep_outfile","a")
        self.broken_outfile = open("broken","a")

        self.VMuserName = ""
        self.VMname = ""
        self.VMuserPassword = ""
        self.VMrootPassword = ""
        self.VMLang = ""
        self.RealMachineUserName = ""
        self.VMIpAdress = ""
        self.machineNames = []
        self.machineNo = 0
        self.testRepo = ""

        self.keyValue = {}


    """ This function gets the virtual box machine names in order to list the machines to user."""
    def get_machineNames(self):
        getMachineNamesCommand  = os.popen("VBoxManage list vms")

        for line in getMachineNamesCommand.readlines():
            if "{" in line:
                machineName = line.split(" ")[0]
                self.machineNames.append(machineName)
        return self.machineNames

    """ This function enables user to choose the machine that he/she wants to work."""
    def chooseMachine(self, machineNames):
        count = 1
        for machine in machineNames:
            print str(count) + "-" + machine
            count += 1

        while(1):
            i = raw_input("Please choose the machine you want to work with\n")
            if int(i) > len(machineNames) or int(i) == 0:
                print "Please write a correct number !"
            elif int(i) <= len(machineNames):
                machineName = machineNames[int(i)-1]
                return i
                break
    """ This function takes the snapshot of the virtual machine the user has chosen."""
    def takeSnapshot(self, machineName):
        os.popen("VBoxManage snapshot " + machineName + " take TestSnapshot")
        time.sleep(0.5)


    """ This function shutdowns the virtual machine that the user has chosen."""
    def shutdownVm(self, machineName):
        os.popen("VBoxManage controlvm " + machineName + " poweroff")
        self.checkState("poweroff", machineName)
        time.sleep(1)


    """ This function starts the virtual machine that the user has chosen."""
    def startVm(self, machineName):
        os.popen("VBoxManage startvm " + machineName)
        self.checkState("running", machineName)

    """ This function revert the current snapshot to its previous state."""
    def goBack(self, machineName):
        os.popen("VBoxManage snapshot " + machineName + " restorecurrent")

    """ This function checks if state is changed."""
    def checkState(self,state, machineName):
        while(1):
            if(str(self.showState(machineName)).find(str(state))):
                break
            else:
                time.sleep(0.5)

    """ This function returns several different states of selected virtaul machine."""
    def showState(self, machineName):
        showStateCommand = os.popen("VBoxManage showvminfo "+ machineName +" --machinereadable")

        for line in showStateCommand.readlines():
            if "VMState=" in line:
                state = line.split("\"")[1]
                #print state.strip()

    """ This function shows if the selected virtual machine network is in Bridged Adapter state."""
    def showBridge(self, machineName):
        showBridgeCommand = os.popen("VBoxManage showvminfo "+ machineName +" --machinereadable")

        for line in showBridgeCommand.readlines():
            if "nic1" in line:
                nic = line.split("\"")[1]
                return nic

    """ This function makes a remote connection to selected virtual machine from user machine."""
    def connectTo(self, mode="normal"):
        if(mode == "normal"):
            self.execute = pexpect.spawn("ssh %s@%s"% ( self.VMuserName, self.VMIpAdress) , timeout=None)
            print "ssh %s@%s "% ( self.VMuserName, self.VMIpAdress)

            if(self.checkKnownHosts() == False):
                print "false"
                self.execute.expect('(yes/no)?')
                self.execute.sendline('yes')
            self.execute.expect('.*ssword:')
            self.execute.sendline(self.VMuserPassword)
            outConnectTo = self.execute.readline()
            if(len(outConnectTo) > 0):
                print "Connection start..."

    """This function checks the known hosts of the real machine"""
    def checkKnownHosts(self):
        file = open("/home/" + self.RealMachineUserName + "/.ssh/known_hosts")
        content = file.read()
        itr = content.find(self.VMIpAdress)
        if(itr == -1):
            return False
        else:
            return True

    """This function sends command to virtaul machine and write the results"""
    def sendCommand(self, command, mode="not_root"):
        VMname = self.VMname

        value = ""
        if(mode == "parse"):
            self.revdepOutput = ""

        self.execute.sendline(command)
        if not "uname" in command:
            print command + "\n"

        if(mode == "close"):
            while(1):
                outSendCommand = self.execute.readline()
                if(outSendCommand.find(VMname) != -1):
                    break
                self.execute.close()
                return
        if(mode == "exit"):
            VMname =  self.VMuserName + "@" + self.VMname
            return

        if(mode == "root"):
            if(self.VMLang == "tr"):
                self.execute.expect('.*rola:')
            else:
                self.execute.expect('.*ssword:')

            self.execute.sendline(self.VMrootPassword)
            VMname = self.VMname
            return

        self.execute.sendline("uname")

        while(1):
            outSendCommand = self.execute.readline()
            #print outSendCommand + "\n"
            if(outSendCommand.find(VMname) != -1):
                break

        while(1):
            outSendCommand = self.execute.readline()
            if not "uname" in outSendCommand:
                print outSendCommand.strip()

            if(outSendCommand.find(VMname) != -1):
                break

            if((outSendCommand.find("uname") == -1) and (outSendCommand.find(VMname) == -1) ):
                if(mode == "parse"):
                    self.revdepOutput += outSendCommand
                elif(mode == "pisilr"):
                    value += outSendCommand
        return value

    """This function remove the repositories in Virtual Box"""
    def removeRepos(self, repos):
        listRepos = []
        repos = repos.split("\n")
        for i in range(len(repos)/2):
            listRepos.append(repos[2*i].split(" ")[0].replace("\x1b[32m", "").strip())

        for i in range(len(listRepos)):
            self.sendCommand("pisi rr %s" % listRepos[i])

    """This function adds the test repository that entered from the console."""
    def addTestRepo(self):
        self.testRepo = raw_input("Please enter the Pardus tester repo that you will use: \n")
        self.sendCommand("pisi ar test %s -y" % self.testRepo)


    """This function check the broken links of the installed files"""
    def reverseChecker(self, machineName):
        ack_file = open("ack", "r")

        for line in ack_file.readlines():
            self.startVm(machineName)
            time.sleep(2)
            self.connectTo()
            self.sendCommand("su -","root")
            self.sendCommand("pisi it %s -y" % line.strip())
            self.sendCommand("revdep-rebuild","parse")
            self.connectTo()
            self.sendCommand("exit","close")
            self.parseOutput()
            self.shutdownVm(machineName)
            time.sleep(1)
            self.goBack(machineName)
        ack_file.close()

    """This function parses the revdep output"""
    def parseOutput(self):

        outParse = self.revdepOutput
        self.revdep_outfile.write(outParse)
        self.revdep_outfile.flush()
        splitted = outParse.split("\n")

        for line in splitted:
            print line
            split_out = line.split(" ")

            if "paket" in line:             # for Turkish
                if not split_out[3].strip().startswith("/"):
                    self.keyValue["/" + split_out[3].strip()] = split_out[0]
                else:
                    self.keyValue[split_out[3].strip()] = split_out[0]

                print self.keyValue
                #print self.keyValue[split_out[3].strip()]
            elif "Package" in line:          # for English
                print split_out[4].strip()
                self.keyValue[split_out[4].strip()] = split_out[1]
                print self.keyValue[split_out[4].strip()]
        for line in splitted:
            print line
            split_out = line.split(" ")

            if "broken" in line and not "libraries" in line:
                print split_out[3]
                readBroken = open("broken", "r")
                if self.keyValue[split_out[3]] + " needs:" not in readBroken.read():
                    self.broken_outfile.write( self.keyValue[split_out[3]] + " needs:")
                    print "Package " + self.keyValue[split_out[3]] + "  has " + split_out[3] + " library so following package(s) needed:"
                    self.broken_outfile.write("-------------------------------------------------------")
                    self.broken_outfile.write("\n")
                    self.broken_outfile.flush()


                    for i  in range(5, len(split_out)):
                        if not ")" in split_out[i]:
                            print "library: " + split_out[i]
                            self.findPackage(split_out[i])
                        else:
                            print "library: " + split_out[i].strip().replace(")", "")
                            self.findPackage(split_out[i].strip().replace(")", ""))

                readBroken.close()

    """This function finds runtime dependent package of the broken link."""
    def findPackage(self,library):
        release = self.testRepo.split("-")[1].split("/")[0]
        #print release

        html = os.popen("curl http://packages.pardus.org.tr/search/pardus-%s/%s/" % (release, library))

        for line in html.readlines():
            #print line
            if "<td><a href=\"/search/pardus-%s/package" % release in line:
                print "package:" + line.split(">")[2].split("<")[0]
                package = line.split(">")[2].split("<")[0]
                self.broken_outfile.write(package)
                self.broken_outfile.write("\n")
                self.broken_outfile.flush()
def  main(argv):
    obj = FindBrokenLinks()
    obj.machineNames = obj.get_machineNames()
    obj.machineNo = obj.chooseMachine(obj.machineNames)

    if(not (obj.showBridge(obj.machineNames[int(obj.machineNo)-1]) == "bridged")):
        print "It seems you still did not configure your Network property into \"bridged\" \n program will exit now"
        exit()

    obj.startVm(obj.machineNames[int(obj.machineNo)-1])

    obj.VMuserName = raw_input("Please enter the virtual machine user name:\n")
    obj.VMname = raw_input("Please enter the virtual machine name:\n")
    obj.VMuserPassword = getpass.unix_getpass("Please enter the virtual machine user Password:\n")
    obj.VMrootPassword = getpass.unix_getpass("Please enter the virtual machine root Password:\n")
    obj.VMLang = raw_input("Please enter the virtual machine language (tr or en):\n")
    obj.RealMachineUserName = raw_input("Please enter the real machine user name:\n")
    obj.VMIpAdress = raw_input("After the VirtualBox has opened, please restart openssh of Real Machine and VirtualMachine and write the virtualMachine ip address and enter to continue:\n")

    # SSH Connection is established
    obj.connectTo()

    # Stable repo updated
    obj.sendCommand("su - ", "root")
    obj.sendCommand("pisi up --ignore-safety -y")
    obj.sendCommand("exit","close")
    obj.shutdownVm(obj.machineNames[int(obj.machineNo)-1])
    time.sleep(4)


    # SSH Connection is established
    obj.startVm(obj.machineNames[int(obj.machineNo)-1])
    obj.connectTo()

    # Stable and contrib repos removed
    obj.sendCommand("su - ", "root")
    repos = obj.sendCommand("pisi lr", "pisilr")
    obj.removeRepos(repos)

    # Tester repo is added
    obj.addTestRepo()
    obj.sendCommand("pisi ur")
    time.sleep(4)

    # Tester repo updated.
    obj.sendCommand("pisi up --ignore-safety -y")
    time.sleep(4)
    #obj.sendCommand("exit","close")
    #obj.shutdownVm(machineNames[int(machineNo)-1])
    obj.takeSnapshot(obj.machineNames[int(obj.machineNo)-1])
    time.sleep(4)
    obj.reverseChecker(obj.machineNames[int(obj.machineNo)-1])


if __name__ == '__main__':
    main(sys.argv)


