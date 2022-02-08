#coded by winteriscoming

import sys
import os


print ("started vgm anayzer script...")

filename=sys.argv[1]

stripheader=0;

print ("input file name is: " + filename)
outfile= filename[0:len(filename)-4]+"_tuned.vgm"


f = open(filename,'r+b')

readdata=b''

newdata=bytearray()

for b in f:
    readdata=readdata+b



totalwritecmds=0
totalfirsttransfercmds=0
totalfrequencycmds=0
totalfrequencycmdsfornoise=0
totalfrequencycmdsneedingtuning=0
total2ndtransfer=0
totalvolumecmds=0

periodicnoise=0

frequencymultiplier=8575/10000

poscheck=0

curChan=0


chanMask=0x60
volMask=0xF
i=0;

if not(stripheader):
    while i<0x40:
        newdata.append(readdata[i])
        i+=1

i=0x40
while i < len(readdata):

    if int(readdata[i])==0x50:
        print ("--------------------------------")
        
        totalwritecmds=totalwritecmds+1
        writedata=readdata[i+1]
        
        curChan=chanMask&writedata;
        curChan=curChan>>5;
        curChan+=1;
        
        print ("Command is for channel : " + str(curChan))
        
        if writedata&0x80:
            #this is a first transfer
            totalfirsttransfercmds=totalfirsttransfercmds+1
            if not (writedata&0x10):
                #this is a cmd for frequency
                totalfrequencycmds+=1
                if not (writedata&0x60==0x60):
                    #this is a cmd for channels 1-3 so it needs a 2nd data byte and needs tuning
                    
                    totalwritecmds+=1;
                    
                    cmdbits=readdata[i+1]&0xF0
                    databits=readdata[i+1]&0x0F
                    
                    highdatabyte=readdata[i+3]&0x3F

                    fullwritedata=databits+(highdatabyte*0x10)
                    
                    frequencyorig=fullwritedata
                    convertedwritedata=int(round(fullwritedata*frequencymultiplier))
                    
                    convertedhighbyte=convertedwritedata>>4
                    convertedlowbyte=convertedwritedata&0xF

                    frequencynew=convertedwritedata
                    highbyte=convertedhighbyte
                    
                    
                    
                    lowbyte=convertedlowbyte+cmdbits
                    
                    print ("cmd: " + hex(readdata[i+0]) +" "+ hex(readdata[i+1])+" "+hex(readdata[i+2]) +" "+ hex(readdata[i+3]))
                    print ("First part: " + "{0:b}".format(readdata[i+1]))
                    print ("Second part: " + "{0:b}".format(readdata[i+3]))
                    
                    if (curChan==3 and periodicnoise):
                        print("This command affects the periodic noise on channel 4")
                        periodicnoise=0
                    
                    newdata.append(readdata[i])
                    newdata.append(lowbyte)
                    newdata.append(readdata[i+2])
                    newdata.append(highbyte)
                    
                    i+=4
                    
                    totalfrequencycmdsneedingtuning+=1
                else:
                    #this is a cmd for channel 4 (noise) and does not have a 2nd data byte
                    print ("cmd: " + hex(readdata[i+0]) +" "+ hex(readdata[i+1]))
                    
                    print ("Noise channel cmd: " + "{0:b}".format(readdata[i+1]))
                    
                    if readdata[i+1] & 0x3 == 0x3:
                        print ("It is a periodic noise command")
                        periodicnoise=1
                    else:
                        periodicnoise=0
                    totalfrequencycmdsfornoise+=1
                    newdata.append(readdata[i])
                    newdata.append(readdata[i+1])
                    
                    
                    i+=2
            else:
                #this is a cmd for volume and does not need a 2nd data byte
                print ("cmd: " + hex(readdata[i+0]) +" "+ hex(readdata[i+1]))
                print ("Volume cmd: " + "{0:b}".format(readdata[i+1]))
                
                volLevel=volMask&readdata[i+1]
                newdata.append(readdata[i])
                newdata.append(readdata[i+1])
                i+=2
                totalvolumecmds+=1
                
                print("Volume level is: " + str(volLevel))
        else:
            #this is a 2nd transfer that should not happen - it means it was not counted as part of a first transfer in the tuning process
            
            print ("Unknown cmd: " + "{0:b}".format(readdata[i+1]))
            newdata.append(readdata[i])
            
            newdata.append(readdata[i+1])
            
            i=i+2
            total2ndtransfer+=1
        
    else:
        #this is some other kind of command
        newdata.append(readdata[i])
        print ("--------------------------------")
        if int(readdata[i])==0x61:
            newdata.append(readdata[i+1])
            newdata.append(readdata[i+2])
            #this is a pause cmd
            
            print("Pause CMD 0x61: " + hex(readdata[i+1]) + " " + hex(readdata[i+2]))
            
            
            i+=2
        if int(readdata[i])==0x66:
            #this is the end of the file and the footer can be stripped
            
            print("End command: " + hex(readdata[i]))
            i=i+1
            break
        if int(readdata[i])==0x62:
            #this is a wait cmd
            print("Wait command: " + hex(readdata[i]))
        print("CMD: " + hex(readdata[i]))
            
            
        i=i+1

        
print ("--------------------------------")
print ("--------------------------------")
print ("--------------------------------")
print ("------------SUMMARY ------------")
print (hex(i) + " total bytes present in vgm file")
print (str(totalwritecmds) + " total write commands present in vgm file")
print (str(totalfirsttransfercmds) + " total first transfers present in vgm file")
print (str(totalvolumecmds) + " total colume cmds present in vgm file")
print (str(totalfrequencycmds) + " total frequency and noise cmds present in vgm file")
print (str(totalfrequencycmdsneedingtuning) + " total frequency cmds for channels 1-3 needing tuning in vgm file")
print (str(totalfrequencycmdsfornoise) + " total cmds for noise in vgm file")
print (str(total2ndtransfer) + " unaccounted 2nd transfers in vgm file")


f.close()
