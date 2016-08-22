"""Sends the relevant commands to the darc-connected NUVU camera"""


class ControlNuvu:
    def __init__(self,prefix="main",cam=0):
        """Prefix: the darc prefix.
        cam: the camera within darc to which these commands should be send.
        """
        self.prefix=prefix
        self.cam=cam

    def sendCommand(self,cmd,checksum=1,raw=[]):
        """Sends command to the camera, with an optional checksum.  Note - the nuvu Windows GUI software always sends the checksum.
        The way to communicate is:
        Send a command, 1 byte at a time, to register 0xB84C.

        raw is a sequence of numbers to be sent directly to this register.  Typically used after the ssva command.

        """
        
        if cmd[-1]!="\n":#add a carriage return.
            cmd+="\n"
        if checksum:#add the commands to tell it to expect a checksum.
            cmd="cc\n"+cmd
            tot=sum(map(ord,cmd))
            if len(raw)>0:
                tot+=sum(raw)
                for r in raw:
                    cmd+=chr(r)
            cmd+="cs %d\n"%tot
        txt=""
        for c in cmd:
            txt+="R[0xB84C]=%d;"%ord(c)
        print "Sending command: %s"%txt
        d=darc.Control(self.prefix)
        d.Set("aravisCmd%d"%self.cam,txt)
    def setTriggerMode(self,mode):
        """Sets trigger mode to:
        0 = internal
        -1 = external (H->L)
        -2 = external exposure
        -3 = external continuous.
        """
        self.sendCommand("stm %d 0"%mode)

    def setAnalogueGain(self,gain):
        """Gain can be 1 or 2.  
        TODO: (possibly higher, check on the GUI)."""
        self.sendCommand("cdsgain %d"%gain)

    def setTemp(self,temp):
        """Set the temperature.  Note, the camera should always be warmed up to -40 before switching off.
        temp is in degrees centigrate.  Can go down to -120.
        """
        self.sendCommand("tsp 1 %d"%temp)

    def setExposureTime(self,exp):
        """Sets exposure time in ms.  0 is free-running.
        TODO: Check - ms or us?"""
        self.sendCommand("se %d"%exp)

    def setROI(self,roi):
        """Sets a region of interest.  Note, currently, only specific ones can be set, since I've not worked out how to set them generally... and haven't had enough time to fully reverse engineer."""
        pass

    def setEMGain(self,gain):
        """Note, requires T<-60.
        Max value 5000.
        """
        if gain<1:
            gain=1
        self.sendCommand("seg %d\r"%gain)


    def setClockRate(self,rate):
        """Rate can be 10 or 20.  (in MHz).
        """
        if rate not in [10,20]:
            raise Exception("Rate must be 10 or 20 MHz")
        if rate==10:
            ld=1
            size=0x80
            unknownData=[0x0,0x3,0x0,0x80]+[0x0]*9+[0x5, 0x0, 0x1]+[0x0]*5+[0x80, 0x0, 0x6, 0x0]
            cdsoffset=7000
        else:
            ld=4
            size=0x88
            unknownData=[0x0,0x1,0x0,0x86]+[0x0]*9+[0x1, 0x0, 0x1, 0x0, 0x2]+[0x0]*3+[0x80,0x0,0x6,0x0]
            cdsoffset=-2000

        self.sendCommand("ld %d"%ld)
        self.sendCommand("sb 4 0")
        self.sendCommand("cdsgain")
        self.sendCommand("cdsoffset")
        self.sendCommand("dsv")
        d=darc.Control(self.prefix)
        d.Set("aravisCmd%d"%self.cam,"xx=0x88;xx=0x88;xx=%d;xx=0x86;"%size)
        self.sendCommand("ssva 12 3\n\n",raw=unknownString)
        self.sendCommand("rsrt")
        self.sendCommand("cdsgain")
        self.sendCommand("cdsgain 1")
        self.sendCommand("rb 4")
        self.sendCommand("sb 4 0")
        self.sendCommand("seg\r")
        self.sendCommand("sw 0")
        self.sendCommand("cdsoffset")
        self.sendCommand("cdsoffset %d"%cdsoffset)
        self.sendCommand("rsrt")

    def set96x96(self,hoffset,voffset):
        """Sets to a 96x96 ROI
        TODO: Calc this stuff."""
        
                         
            
