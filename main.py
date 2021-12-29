"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
--- Nokia 1830 PSS SWDM Performance Collection Tool
--- Created by Naseredin aramnejad
--- Tested on Python 3.7.x
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#___________________________________IMPORTS_____________________________________
import tkinter as tk
from tkinter import ttk
from tkintertable import TableModel
from tkintertable import TableCanvas
from multiprocessing import freeze_support
from multiprocessing import Pool
from multiprocessing import Process
from threading import Thread
from webbrowser import open_new
from telnetlib import Telnet
from sys import exit
from time import sleep
from hashlib import md5
from ast import literal_eval
from datetime import datetime
from os import mkdir,chdir
#___________________________________GLOBALS_____________________________________
_version_ = 2.20
NodeCounter = 0
stepSize = 0
isTrial = True
Templates = []
Network_Data = []
Collected_Data = []
verifyResult = False
processQTY = 1
tableData = {}
results = []
standard_WDM_Events = ('All','Admin State',
                        'Operation State',
                        'LED Status',
                        'RX Power',
                        'TX Power',
                        'Facility Loopback',
                        'Terminal Loopback',
                        'Laser Temperature',
                        'TX Frequency',
                        'RX Frequency',
                        'Pre-FEC BER',
                        'Post-FEC BER')
standard_ETH_Events = ('All','Rx Broadcast Packets',
                        'Rx Collisions',
                        'Rx CRC Alignment Errors',
                        'Rx Drop Events',
                        'Rx Fragments',
                        'Rx Multicast Packets',
                        'Rx Octets',
                        'Rx Oversized Packets',
                        'Rx Packet Error Ratio',
                        'Rx Packets',
                        'Rx Packets 1024 to 1518 Bytes',
                        'Rx Packets 128 to 255 Bytes',
                        'Rx Packets 256 to 511 Bytes',
                        'Rx Packets 512 to 1023 Bytes',
                        'Rx Packets 64 Bytes',
                        'Rx Packets 65 to 127 Bytes',
                        'Rx Undersized Packets',
                        'Tx Broadcast Packets',
                        'Tx Collisions',
                        'Tx CRC Alignment Errors',
                        'Tx DropEvents',
                        'Tx Fragments',
                        'Tx Multicast Packets',
                        'Tx Octets',
                        'Tx Oversized Packets',
                        'Tx Packets',
                        'Tx Packet Error Ratio',
                        'Tx Packets 1024 to 1518 Bytes',
                        'Tx Packets 128 to 255 Bytes',
                        'Tx Packets 256 to 511 Bytes',
                        'Tx Packets 512 to 1023 Bytes',
                        'Tx Packets 64 Bytes',
                        'Tx Packets 65 to 127 Bytes',
                        'Tx Undersized Packets')
standard_OSC_OPT_Events = ('Transmit Power Average',)
standard_OSC_OPR_Events = ('Receive Power Average',)
#_______________________________Rotating BPar Class_(Indeterminate)_____________
class Rotbar:
    def __init__(self,parent,speed=0.05,
                 aspect=1,row=0,column=0,
                 padx=0,pady=0,file='',sticky1='nw',columnspan=1,rowspan=1):
        self.speed = speed
        self.aspect = aspect
        self.parent = parent
        self.filepath = file
        self.row = row
        self.column = column
        self.padx = padx
        self.pady = pady
        self.sticky1 = sticky1
        self.columnspan = columnspan
        self.rowspan = rowspan
        self.label = ttk.Label(self.parent)

    def init(self):
        self.Status = True
        self.label.grid(row=self.row,column=self.column,padx=self.padx,
                        pady=self.pady,sticky=self.sticky1,
                        columnspan=self.columnspan,rowspan=self.rowspan)

    def gif_to_list(self,gif):
        l1,i = [],1
        while True:
            try:
                l1.append(tk.PhotoImage(file=gif,format = f'gif -index {i}'))
                i += 1
            except tk.TclError:
                return l1

    def execute(self):
        piclist = self.gif_to_list(self.filepath)
        while True:
            if self.Status == True:
                for i in piclist:
                    i = i.subsample(self.aspect,self.aspect)
                    self.label.configure(image=i)
                    self.parent.update()
                    sleep(self.speed)
            else:
                break

    def stop(self):
        self.label.grid_forget()
        self.Status = False
#_______________________________NE Adapter Class________________________________
class NE_Adapter:
    def __init__(self , NodeIP , NodeLogin , Commands,port=23):
        self.NodeIP = NodeIP
        self.port = port
        self.NodeLogin = NodeLogin
        self.Commands = Commands
        self.CommandsResult = {}
        self.CollectionStatus = False
        self.tn = Telnet()

        if self.Conn_Init() == True:
            for i in self.Commands:
                self.CommandsResult[i] = self.CMD_Exec(i)
            self.Conn_Terminator()
            self.CollectionStatus = True
        else:
            print(self.NodeIP + ' is not Reachable')

    def Conn_Init(self):
        try:
            self.tn.open(self.NodeIP,self.port,timeout=3)
            self.tn.read_until(b'login:')
            self.tn.write((self.NodeLogin[0] + "\n").encode('ascii'))
            self.tn.read_until(b'Username: ')
            self.tn.write((self.NodeLogin[1] + "\n").encode('ascii'))
            self.tn.read_until(b'Password: ')
            self.tn.write((self.NodeLogin[2] + "\n").encode('ascii'))
            self.tn.read_until(b'(Y/N)?')
            self.tn.write(('y' + "\n").encode('ascii'))
            self.tn.read_until(b'#')
            self.tn.write(('paging status disabled' + "\n").encode('ascii'))
            self.tn.read_until(b'#')
            return True
        except:
            return False

    def CMD_Exec(self,cmd):
        self.tn.write((cmd + "\n").encode('ascii'))
        data = self.tn.read_until(b"#")
        return data.decode('utf-8')

    def Conn_Terminator(self):
        self.tn.write(('logout\n').encode('ascii'))
        self.tn.close()
#_______________________________Custom TextBox Class____________________________
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, *args):
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)
        if (args[0] in ("insert", "delete") or
            args[0:3] == ("mark", "set", "insert")):
            self.event_generate("<<CursorChange>>", when="tail")
        return result
#_______________________________New Template Class______________________________
class Template_Builder:
    def __init__(self,name=None,lstSelectedEvents=None,lstTempl=None):
        self.name = name
        if name != None:
            self.events = self.EventCollector(lstSelectedEvents)
            self.ports = self.PortCollector(lstTempl)
            self.Commands = self.CMDGen()
        elif name == None:
            self.events = None
            self.ports = None
            self.Commands = None

    def EventCollector(self,lstSelectedEvents):
        event_list = {}
        for i in lstSelectedEvents:
            tmp = i.split('•••')
            if tmp[0] not in event_list:
                event_list[tmp[0]] = []
            event_list[tmp[0]].append(tmp[1])
        return event_list

    def PortCollector(self,lstTempl):
        tmpl = {}
        for i in lstTempl:
            tmp = i.split('•••')
            if tmp[1] not in tmpl:
                tmpl[tmp[1]] = []
            tmpl[tmp[1]].append(tmp[2]+'•••'+tmp[3])
        return tmpl

    def CMDGen(self):
        Commands = {}
        for i in self.ports:
            for j in self.ports[i]:
                tmp = j.split('•••')
                if i not in Commands:
                    Commands[i] = []
                Commands[i].append('show interface ' + tmp[0] + ' '+tmp[1] +
                                                                    ' detail')
        if 'Ethernet' in self.events:
            for i in self.ports:
                for j in self.ports[i]:
                    tmp = j.split('•••')
                    if i not in Commands:
                        Commands[i] = []
                    Commands[i].append('show interface '+tmp[0]+' '+tmp[1]+
                                                    ' PM ethernet 0 0')
        if 'OSC_OPT' in self.events:
            for i in self.ports:
                for j in self.ports[i]:
                    tmp = j.split('•••')
                    if i not in Commands:
                        Commands[i] = []
                    Commands[i].append('show interface '+tmp[0]+' '+tmp[1]+
                                                    ' PM opt 0 0')
        if 'OSC_OPR' in self.events:
            for i in self.ports:
                for j in self.ports[i]:
                    tmp = j.split('•••')
                    if i not in Commands:
                        Commands[i] = []
                    Commands[i].append('show interface '+tmp[0]+' '+tmp[1]+
                                                    ' PM opr 0 0')
        return(Commands)
#_______________________________________________________________________________
def LoadCards():
    btnLoadCard.grid_forget()
    if cmbNetData.get() != '':
        valid_cards = ['20MX80','20AX200','1UX100','2UX200','11DPM12','11DPM8',
                       '12P120','30AN300','4UC400','4AN400','2UC400','AHPHG',
                       'IROADMV','AHPLG','A2325A']
        login = []
        Cardlist = []
        nodeip = cmbNetData.get().split('•••')[1]
        for i in Network_Data:
            if i[1] == nodeip:
                login.append(i[2])
                login.append(i[3])
                login.append(i[4])
                break
        Command = ['show slot *']
        obj = NE_Adapter(nodeip,login,Command)
        if obj.CollectionStatus == False:
            pbar1.stop()
            btnLoadCard.grid(column=2,row=3,padx=(0,5),sticky='nw')
            return
        Cards = obj.CommandsResult[Command[0]].splitlines()
        del(obj)
        for i in Cards:
            if '/' in i:
                l0 = i.find(' ',i.find('/'))
                tmp = i[l0+1:i.find('  ',l0)]
                if tmp in valid_cards:
                    Cardlist.append(tmp)
        Cardlist = sorted(Cardlist)
        cmbCards.config(state='readonly')
        cmbCards['values'] = tuple(set(Cardlist))
        cmbCards.set(cmbCards['values'][0])
        pbar1.stop()
        btnLoadCard.grid(column=2,row=3,padx=(0,5),sticky='nw')
    else:
        tk.messagebox.showerror('Error','Select the node first!')
#_______________________________________________________________________________
def Init_Interface(event):
    if OnlineVar.get() == 2:
        cmbInterfaces['values'] = ()
        cmbInterfaces.set('')
        cmbInterfaces.config(state='disabled')
#_______________________________________________________________________________
def Init_Shelfs(event):
    if OnlineVar.get() == 2:
        cmbCards['values'] = ()
        cmbCards.set('')
        cmbCards.config(state='disabled')
        Init_Interface(event)
#_______________________________________________________________________________
def LoadInts():
    btnLoadInt.grid_forget()
    if cmbCards.get() != '':
        login = []
        Intlist = []
        nodeip = cmbNetData.get().split('•••')[1]
        for i in Network_Data:
            if i[1] == nodeip:
                login.append(i[2])
                login.append(i[3])
                login.append(i[4])
                break
        Command = ['show interface ' + cmbCards.get() + ' *']
        obj = NE_Adapter(nodeip,login,Command)
        if obj.CollectionStatus == False:
            pbar2.stop()
            btnLoadInt.grid(column=2,row=4,padx=(0,5),sticky='nw')
            return
        Cards = obj.CommandsResult[Command[0]].splitlines()
        del(obj)
        for i in Cards:
            if '/' in i:
                l0 = i.find('/')
                tmp = i[l0-1:i.find(' ',l0)]
                if cmbCards.get() not in ['ahplg','AHPLG','iroadmv',
                                          'IROADMV','ahphg','AHPHG','a2325a',
                                          'A2325A']:
                    Intlist.append(tmp)
                else:
                    if 'OSC' in tmp:
                        Intlist.append(tmp)
        cmbInterfaces.config(state='readonly')
        cmbInterfaces['values'] = tuple(Intlist)
        cmbInterfaces.set(cmbInterfaces['values'][0])
        pbar2.stop()
        btnLoadInt.grid(column=2,row=4,padx=(0,5),sticky='nw')
    else:
        tk.messagebox.showerror('Error','Select the card first!')
#_______________________________________________________________________________
def GoOffline():
    btnLoadInt.config(state='disable')
    btnLoadCard.config(state='disable')
    cmbShelfs.config(state='readonly')
    cmbCards.config(state='readonly')
    cmbInterfaces.grid_forget()
    txtPortAdd.grid(column=1,row=4,padx=(0,10),sticky='nw')
#_______________________________________________________________________________
def GoOnline():
    cmbShelfs.set('')
    cmbCards.set('')
    cmbInterfaces.set('')
    btnLoadInt.config(state='normal')
    btnLoadCard.config(state='normal')
    cmbShelfs.config(state='disable')
    cmbCards.config(state='disable')
    cmbInterfaces.config(state='disable')
    txtPortAdd.grid_forget()
    cmbInterfaces.grid(column=1,row=4,padx=(0,10),sticky='nw')
#_______________________________________________________________________________
def TableExport(meth='Manual'):
    folderflag = False
    global tableData
    titleflag = False
    if meth=='Manual':
        filename = tk.filedialog.asksaveasfile(mode='w',defaultextension=".csv",
                        filetypes = (("CSV files","*.csv"),("all files","*.*")))
        if filename == None:
            return
    elif meth=='Auto':
        try:
            chdir(log_Folder)
            folderflag = True
        except:
            print('Couldn\'t switch to the log folder...')
            pass
        datetimeobj = datetime.now()
        currentdatetime = str(datetimeobj.year)+str(datetimeobj.month)+\
        str(datetimeobj.day)+str(datetimeobj.hour)+str(datetimeobj.minute)+\
        str(datetimeobj.second)
        filename_name = 'Performance_Export_'+ currentdatetime+'.csv'
        filename = open(filename_name,'w')
    for i in tableData:
        if titleflag == False:
            for j in tableData[i]:
                filename.write(str(j)+',')
            filename.write('\n')
            titleflag = True
        for j in tableData[i]:
            filename.write(str(tableData[i][j])+',')
        filename.write('\n')
    filename.close()
    if folderflag == True:
        chdir('..')
        folderflag = False
#______________________________ Process QTY Update _____________________________
def updateValue(e):
    global processQTY
    tmp = scaleVal.get()
    lblCurrentPrQtyValue.config(text=str(int((tmp))))
    processQTY = int(tmp)
#______________________________Event Extractor Function_________________________
def event_Selector(cardinfo,standard_event):
    global standard_WDM_Events , standard_ETH_Events, standard_OSC_OPT_Events
    global standard_OSC_OPR_Events
    ethernet_events = {'Rx Broadcast Packets':'Rx Broadcast Packets',
                       'Rx Collisions':'Rx Collisions',
                       'Rx CRC Alignment Errors':'Rx CRC Alignment Errors',
                       'Rx Drop Events':'Rx Drop Events',
                       'Rx Fragments':'Rx Fragments',
                       'Rx Multicast Packets':'Rx Multicast Packets',
                       'Rx Octets':'Rx Octets',
                       'Rx Oversized Packets':'Rx Oversized Packets',
                       'Rx Packet Error Ratio':'Rx Packet Error Ratio',
                       'Rx Packets':'Rx Packets',
                       'Rx Packets 1024 to 1518 Bytes':'Rx Packets 1024 to 1518 Bytes',
                       'Rx Packets 128 to 255 Bytes':'Rx Packets 128 to 255 Bytes',
                       'Rx Packets 256 to 511 Bytes':'Rx Packets 256 to 511 Bytes',
                       'Rx Packets 512 to 1023 Bytes':'Rx Packets 512 to 1023 Bytes',
                       'Rx Packets 64 Bytes':'Rx Packets 64 Bytes',
                       'Rx Packets 65 to 127 Bytes':'Rx Packets 65 to 127 Bytes',
                       'Rx Undersized Packets':'Rx Undersized Packets',
                       'Tx Broadcast Packets':'Tx Broadcast Packets',
                       'Tx Collisions':'Tx Collisions',
                       'Tx CRC Alignment Errors':'Tx CRC Alignment Errors',
                       'Tx DropEvents':'Tx DropEvents',
                       'Tx Fragments':'Tx Fragments',
                       'Tx Multicast Packets':'Tx Multicast Packets',
                       'Tx Octets':'Tx Octets',
                       'Tx Oversized Packets':'Tx Oversized Packets',
                       'Tx Packet Error Ratio':'Tx Packet Error Ratio',
                       'Tx Packets':'Tx Packets',
                       'Tx Packets 1024 to 1518 Bytes':'Tx Packets 1024 to 1518 Bytes',
                       'Tx Packets 128 to 255 Bytes':'Tx Packets 128 to 255 Bytes',
                       'Tx Packets 256 to 511 Bytes':'Tx Packets 256 to 511 Bytes',
                       'Tx Packets 512 to 1023 Bytes':'Tx Packets 512 to 1023 Bytes',
                       'Tx Packets 64 Bytes':'Tx Packets 64 Bytes',
                       'Tx Packets 65 to 127 Bytes':'Tx Packets 65 to 127 Bytes',
                       'Tx Undersized Packets':'Tx Undersized Packets'}
    osc_events = {'wdm':{'Admin State':'Admin State',
                         'Operation State':'Oper State',
                         'LED Status':'Status LED',
                         'RX Power':'Received Power',
                         'TX Power':'Transmitted Power',
                         'Facility Loopback':'Facility Loopback',
                         'Terminal Loopback':'Terminal Loopback',
                         'TX Frequency':'Channel Tx',
                         'RX Frequency':'Channel Rx',
                         'Laser Temperature':'Laser Case Temperature',
                         'Pre-FEC BER':'PreFecBer',
                         'Post-FEC BER':'PostFecBer'},
                  'ethernet':ethernet_events,
                  'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                  'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_4uc400 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_30an300 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_4an400 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_2uc400 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_20ax200 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_20mx80 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_1ux100 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_2ux200 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Laser Temperature':'Laser Case Temperature',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_12p120 = {'wdm':{'Admin State':'Admin State',
                           'Operation State':'Oper State',
                           'LED Status':'Status LED',
                           'Laser Temperature':'Laser Temperature',
                           'TX Power':'Transmitted Power',
                           'RX Power':'Received Power',
                           'TX Frequency':'Channel Tx',
                           'RX Frequency':'Channel Rx',
                           'Pre-FEC BER':'PreFecBer',
                           'Post-FEC BER':'PostFecBer',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_11dpm12 = {'wdm':{'Admin State':'Admin State',
                            'Operation State':'Oper State',
                            'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'ChannelTx',
                           'RX Frequency':'ChannelRx',
                           'Pre-FEC BER':'Pre-Fec BER',
                           'Post-FEC BER':'Post-Fec BER',
                           'Laser Temperature':'Laser Temperature'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Event_11dpm8 = {'wdm':{'Admin State':'Admin State',
                            'Operation State':'Oper State',
                            'LED Status':'Status LED',
                           'RX Power':'Received Power',
                           'TX Power':'Transmitted Power',
                           'Facility Loopback':'Facility Loopback',
                           'Terminal Loopback':'Terminal Loopback',
                           'TX Frequency':'ChannelTx',
                           'RX Frequency':'ChannelRx',
                           'Pre-FEC BER':'Pre-Fec BER',
                           'Post-FEC BER':'Post-Fec BER',
                           'Laser Temperature':'Laser Temperature'},
                     'ethernet':ethernet_events,
                     'OSC_OPT':{'Transmit Power Average':'OPT Average (dBm)'},
                     'OSC_OPR':{'Receive Power Average':'OPR Average (dBm)'}}

    Card_List = {'1ux100':Event_1ux100,'1UX100':Event_1ux100,
                     '20mx80':Event_20mx80,'20MX80':Event_20mx80,
                     '20AX200':Event_20ax200,'20ax200':Event_20ax200,
                     '4uc400':Event_4uc400,'4UC400':Event_4uc400,
                     '2uc400':Event_2uc400,'2UC400':Event_2uc400,
                     '2ux200':Event_2ux200,'2UX200':Event_2ux200,
                     '30AN300':Event_30an300,'30an300':Event_30an300,
                     '4AN400':Event_4an400,'4an400':Event_4an400,
                     '12p120':Event_12p120,'12P120':Event_12p120,
                     '11dpm12':Event_11dpm12,'11DPM12':Event_11dpm12,
                     '11DPM8':Event_11dpm8,'11dpm8':Event_11dpm8,
                     'ahphg':osc_events,'ahplg':osc_events,'iroadmv':osc_events,
                     'AHPHG':osc_events,'AHPLG':osc_events,'IROADMV':osc_events,
                     'a2325a':osc_events,'A2325A':osc_events}
    Eventtype = ''
    cardType = ''
    if standard_event in standard_WDM_Events:
        Eventtype = 'wdm'
    elif standard_event in standard_OSC_OPT_Events:
        Eventtype = 'OSC_OPT'
    elif standard_event in standard_OSC_OPR_Events:
        Eventtype = 'OSC_OPR'
    elif standard_event in standard_ETH_Events:
        Eventtype = 'ethernet'

    for i in Card_List:
        if i in cardinfo:
            cardType = i
            break

    if cardType != '':
        specific_event = Card_List[cardType][Eventtype][standard_event]
        return (specific_event)
    else:
        return ''
#________________________________ Event Selector _______________________________
def port_perf(portinfo,event):
    tmp = portinfo.splitlines()
    target = event_Selector(tmp[0] , event)
    l0 = l1 = l2 = 0
    lineofs = ''
    foundit = False
    for i in tmp:
        if target in i:
            foundit = True
            lineofs = i
            l0 = i.find(target)
            break
    if foundit == True:
        l1 = lineofs.find(":",l0) + 1
        l2=lineofs.find("  ",l1)
        if (l2 == -1 or 'ethernet' in tmp[0] or 'PM op' in tmp[0]) and\
         ('OSCSFP detail' not in tmp[0]):
            result = lineofs[l1:].strip()
        elif 'OSCSFP detail' in tmp[0]:
            l1 = lineofs.find(target)
            l2 = lineofs.find(":",l1)+1
            l3 = lineofs.find("  ",l2+1)
            if l3 == -1:
                result = lineofs[l2:].strip()
            else:
                result = lineofs[l2:l3].strip()
        else:
            result = lineofs[l1:l2+1].strip()
        return result
    else:
        return ''
#   _________________________Tab3 Table loader__________________________________
def TableUpdate(TemplateOBJ):
    print('entered!')
    global Collected_Data , tableData
    tableData = {}
    extraction_dic = {}
    current_Collected_OBJ = None
    for L in TemplateOBJ.ports:
        for f in Collected_Data:
            if f.NodeIP == L:
                current_Collected_OBJ = f
                break
        if current_Collected_OBJ.CollectionStatus == True:
            for j in TemplateOBJ.ports[L]:
                current_command = []
                list1=j.split('•••')
                for k in TemplateOBJ.Commands[L]:
                    if (list1[0] + ' ' + list1[1]) in k:
                        current_command.append(k)
                for s in current_command:
                    if (L+'•••'+j) not in extraction_dic:
                        extraction_dic[L+'•••'+j] = {}
                    extraction_dic[L+'•••'+j][s] = current_Collected_OBJ.CommandsResult[s]
        else:
            print(current_Collected_OBJ.NodeIP, 'Is not Collected, Skipping...')
            continue
    Port_QTY = len(extraction_dic)
    try:
        if Port_QTY > 0:
            for i in range(1,Port_QTY+1):
                tableData[i] = {}
            counter = 0
            for h in extraction_dic:
                counter += 1
                tableData[counter]['Port'] = h
                if 'WDM' in TemplateOBJ.events:
                    for m in TemplateOBJ.events['WDM']:
                        tmp = [x for x in extraction_dic[h] if 'detail' in x][0]
                        current_port_info1 = extraction_dic[h][tmp]
                        tableData[counter][m] = port_perf(current_port_info1,m)
                if 'Ethernet' in TemplateOBJ.events:
                    for m in TemplateOBJ.events['Ethernet']:
                        tmp = [x for x in extraction_dic[h] if 'PM ethernet 0' in x][0]
                        current_port_info2 = extraction_dic[h][tmp]
                        tableData[counter][m] = port_perf(current_port_info2,m)
                if 'OSC_OPT' in TemplateOBJ.events:
                    for m in TemplateOBJ.events['OSC_OPT']:
                        tmp = [x for x in extraction_dic[h] if 'PM opt' in x][0]
                        current_port_info3 = extraction_dic[h][tmp]
                        tableData[counter][m] = port_perf(current_port_info3,m)
                if 'OSC_OPR' in TemplateOBJ.events:
                    for m in TemplateOBJ.events['OSC_OPR']:
                        tmp = [x for x in extraction_dic[h] if 'PM opr' in x][0]
                        current_port_info4 = extraction_dic[h][tmp]
                        tableData[counter][m] = port_perf(current_port_info4,m)
            table = TableCanvas(lblFrame6, data=tableData,width=670,height=273)
            table.grid_configure(padx=(1,6))
            table.show()
            btnExport.config(state='normal')
            TableExport('Auto')
        else:
            print('All Nodes are unreachable!')
            btnExport.config(state='disabled')
            pass
    except:
        pass
#   ________________________NE Communicator_____________________________________
def P_Executer(Node_Info):
    global NodeCounter
    NodeCounter += 1
    print(str(NodeCounter) + ") "+ Node_Info[0] ,' Started...')
    NodeObject =  NE_Adapter(Node_Info[0],[Node_Info[2],Node_Info[3],
                                                Node_Info[4]],Node_Info[1])
    print(str(NodeCounter) + ") "+ Node_Info[0] ,' Finished!')
    return NodeObject
# ______________________NE Communication Multiprocessing________________________
def collect_result(res):
    global Collected_Data,stepSize
    progress.step(stepSize)
    Collected_Data.append(res)
# ______________________NE Communication Multiprocessing________________________
def NE_Collection_Initiator(All_Nodes,TemplateOBJ):
    btnExecute.grid_forget()
    global stepSize
    global Collected_Data,NodeCounter,processQTY
    stepSize = int(1000/len(All_Nodes))
    NodeCounter = 0
    lblCollectionStatusResult.configure(text='In Progress ',foreground='orange')
    btnExecute.configure(state='disable')
    p = Pool(int(processQTY))
    for i in All_Nodes:
        p.apply_async(P_Executer,args=(i,), callback=collect_result)
    p.close()
    p.join()
    pbar3.stop()
    btnExecute.grid(row=0,column=2,sticky='wn',padx=5,pady=5,columnspan=2)
    btnExecute.configure(state='normal')
    lblCollectionStatusResult.configure(text='Done ',foreground='green')
    TableUpdate(TemplateOBJ)
#   _________________________Perf Collector_____________________________________
def Collector():
    global Templates
    global Collected_Data,Network_Data
    progressVar.set(0)
    Collected_Data = []
    all_nodes = []
    if cmbTemplateList.get() != '':
        Templatename = cmbTemplateList.get()
        for i in Templates:
            if i.name == Templatename:
                TemplateOBJ = i
        for j in TemplateOBJ.Commands:
            node_info = []
            node_info.append(j)
            node_info.append(TemplateOBJ.Commands[j])
            for i in Network_Data:
                if i[1] == j:
                    node_info.append(i[2])
                    node_info.append(i[3])
                    node_info.append(i[4])
            all_nodes.append(node_info)
        NE_Collection_Initiator(all_nodes,TemplateOBJ)
    else:
        tk.messagebox.showerror('Error','Select the desired template first')
#_______________________________________________________________________________
def ActivatePbar(pbar):
    pbar.init()
    pbar.execute()
#_______________________________________________________________________________
def Proc_Pbar(pbar,proc):
    Thread(target=ActivatePbar,args=[pbar]).start()
    Thread(target=proc).start()
#   ________________________Event add to Listbox________________________________
def Add2Event():
    if cmbEventType.get() != '':
        if cmbSelectedEvents.get() != '':
            if cmbSelectedEvents.get() != 'All':
                event = cmbEventType.get()+'•••'+cmbSelectedEvents.get()
                if event not in lstSelectedEvents.get(0 , 'end'):
                    lstSelectedEvents.insert('end',
                    cmbEventType.get() + '•••' + cmbSelectedEvents.get())
                else:
                    tk.messagebox.showinfo('Error','The event is already selected!')
            else:
                for i in cmbSelectedEvents['values']:
                    if i != 'All':
                        event = cmbEventType.get() + '•••' + i
                        if event not in lstSelectedEvents.get(0 , 'end'):
                            lstSelectedEvents.insert('end',event)
        else:
            tk.messagebox.showinfo('Error','Select the event first!')
    else:
        tk.messagebox.showinfo('Error','Select the event type first!')
#   ________________________Event ComboBox Content______________________________
def cmbEventTypeOnSelect(event):
    global standard_ETH_Events,standard_WDM_Events,standard_OSC_OPT_Events
    global standard_OSC_OPR_Events
    standard_ETH_Events = sorted(standard_ETH_Events)
    standard_WDM_Events = sorted(standard_WDM_Events)
    if cmbEventType.get() == 'Ethernet':
        cmbSelectedEvents.set('')
        cmbSelectedEvents['values'] = standard_ETH_Events
    elif cmbEventType.get() == 'WDM':
        cmbSelectedEvents.set('')
        cmbSelectedEvents['values'] = standard_WDM_Events
    elif cmbEventType.get() == 'OSC_OPT':
        cmbSelectedEvents.set('')
        cmbSelectedEvents['values'] = standard_OSC_OPT_Events
    elif cmbEventType.get() == 'OSC_OPR':
        cmbSelectedEvents.set('')
        cmbSelectedEvents['values'] = standard_OSC_OPR_Events
#   _________________________Port Input Validator_______________________________
def PortFormatVerify(PortInput):
    LinePortQTY = {'2UC400':2,'4UC400':4,'20UC200':20,'30AN300':30,'4AN400':4,
                    '20AN80':20,'30SE300':30,'6SE300':6,'20MX80':20,'1UX100':1,
                    '2UX200':2,'4AX200':4,'20AX200':20,'11DPM12':2,'12P120':6,
                    '11QCE12X':4,'11OPE8':6,'11DPM8':2}
    ClientPortQTY = {'11DPM12':12,'12P120':6,'11QCE12X':23,'11OPE8':2,
                    '11DPM8':8}
    try:
        temp = PortInput.split('/')
        if len(temp) != 3:
            return 'invalid'
        if cmbShelfs.get() == '1830 PSS-8/16II/32':
            if int(temp[0]) not in range(1,25) or\
               int(temp[1]) not in range(1,33):
               return 'invalid'
            if cmbCards.get() == '11QCE12X' or cmbCards.get() == '11OPE8':
                if (temp[2][0]) in 'xX':
                    if int(temp[2][1:]) in range(1,LinePortQTY[cmbCards.get()]+1):
                        return 'valid'
                    return 'invalid'
                return 'invalid'
            elif cmbCards.get() == 'IROADMV':
                if temp[2].strip().upper() != 'OSCSFP':
                    return 'invalid'
            else:
                if (temp[2][0]) in 'cC':
                    if int(temp[2][1:]) not in range(1, ClientPortQTY[cmbCards.get()]+1):
                       return 'invalid'
                elif (temp[2][0]) in 'lL':
                    if int(temp[2][1:]) not in range(1,LinePortQTY[cmbCards.get()]+1):
                       return 'invalid'
                else:
                    return 'invalid'
            return 'valid'
        else:
            if int(temp[0]) not in range(1,25) or\
               int(temp[1]) not in range(1,25) or\
               int(temp[2]) not in range(1,LinePortQTY[cmbCards.get()]+1):
               return 'invalid'
            return 'valid'
    except:
        return 'invalid'
#   __________________________New Template On Click Function ___________________
def NewTemplate():
    global Templates
    if len(lstTempl.get(0,'end')) > 0:
        if len(lstSelectedEvents.get(0,'end')) > 0:
            answer = tk.simpledialog.askstring("Information","Template Name? ",
                                                                    parent=root)
            if answer == '' or answer == None:
                tk.messagebox.showinfo('Wrong Name','The template name is not valid')
                return
            tmp = Template_Builder(answer,
                        lstSelectedEvents.get(0,'end'),lstTempl.get(0,'end'))
            Templates.append(tmp)
            tabs.tab(2,state='normal')
            lstTempl.delete(0,'end')
            lstSelectedEvents.delete(0,'end')
            cmbShelfs.set('')
            cmbCards.set('')
            txtPortAdd.delete('1.0', "end")
            txtPortAdd.insert("end", r'ex: 1/4/28')
            txtPortAdd.configure(foreground='gray',background='white')
            cmbEventType.set('')
            cmbSelectedEvents.set('')
        else:
            tk.messagebox.showinfo('Error','Event list is Empty!')
    else:
        tk.messagebox.showinfo('Error','Port list is empty!')
    tmplist = []
    if len(Templates) > 0:
        cmbTemplateList['values'] = ()
        for i in Templates:
            tmplist.append(i.name)
    cmbTemplateList['values'] = tuple(tmplist)
#   ____________________________Delete Selected Port____________________________
def DeletePort():
    selection = lstTempl.curselection()
    if selection:
        lstTempl.delete(selection)
    else:
        tk.messagebox.showinfo("Nothing to delete!","Select the port first!")
#   ___________________________Delete Selected Event____________________________
def DeleteEvent():
    selection = lstSelectedEvents.curselection()
    if selection:
        lstSelectedEvents.delete(selection)
    else:
        tk.messagebox.showinfo("Nothing to delete!","Select the event first!")
#   ____________________________Port add to ListBox_____________________________
def Add2Port():
    if cmbNetData.get() != '':
        if OnlineVar.get() == 1:
            if cmbShelfs.get() != '':
                if PortFormatVerify(txtPortAdd.get('1.0','end-1c')) == 'valid':
                    PortInfo = (cmbNetData.get()+'•••'+cmbCards.get()+
                                            '•••'+txtPortAdd.get('1.0','end-1c'))
                    if PortInfo not in lstTempl.get(0,'end'):
                        lstTempl.insert('end',PortInfo)
                    else:
                        tk.messagebox.showinfo("Item Exists!",
                                        "The port combination already exists!")
                else:
                    tk.messagebox.showinfo("Error",
                                    "The entered port address is not valid!")
            else:
                tk.messagebox.showinfo("Error",
                                    "Select the shelf type first!")
        else:
            if cmbCards.get() != '':
                if cmbInterfaces.get() != '':
                    PortInfo = (cmbNetData.get()+'•••'+cmbCards.get()+
                                                    '•••'+cmbInterfaces.get())
                    if PortInfo not in lstTempl.get(0,'end'):
                        lstTempl.insert('end',PortInfo)
                    else:
                        tk.messagebox.showinfo("Item Exists!",
                                        "This port combination already exists!")
                else:
                    tk.messagebox.showinfo("Error","Select the interface first!")
            else:
                tk.messagebox.showinfo("Error","Select the card first!")
    else:
        tk.messagebox.showinfo("Error",
                            "Select the node first!")
#   ____________________________Shelf Type Select_______________________________
def ShelfOnSelect(event):
    if cmbShelfs.get() == '1830 PSS-24x':
        cmbCards.set('')
        cmbCards['values'] = ('2UC400','4UC400','4AN400','30AN300')
        cmbCards.set('4UC400')
    elif cmbShelfs.get() == '1830 PSS-8x/12x':
        cmbCards.set('')
        cmbCards['values'] = ('20AX200','1UX100','20MX80','2UX200')
        cmbCards.set('20AX200')
    elif cmbShelfs.get() == '1830 PSS-8/16II/32':
        cmbCards.set('')
        cmbCards['values'] = ('11DPM12','12P120','11DPM8','IROADMV')
        cmbCards.set('11DPM12')
#   ____________________________Browse On Click Function _______________________
def btnBrowseCall():
    btnBrowse.focus()
    txtPath.delete('1.0','end-1c')
    txtPath.insert('1.0',tk.filedialog.askopenfilename(initialdir='C:\\',
                    title = "Select file",
                    filetypes = (("CSV files","*.csv"),("all files","*.*"))))
    txtPath.configure(foreground='black')
#   ____________________________Verify On Click Function _______________________
def btnVerifyCall():
    global Network_Data , verifyResult
    btnVerify.focus()
    Network_Data = []
    verifyResult = True
    filepath = txtPath.get('1.0','end-1c')
    try:
        with open(filepath) as file:
            content = file.read().splitlines()
            for i in content[1:]:
                try:
                    tmp = i.split(',')
                    tmp1 = tmp[1].strip().split('.')
                    if (len(tmp) != 5) or (tmp[0].strip() == '') or\
                       (tmp[1].strip() == '') or (tmp[2].strip() == '') or\
                       (tmp[3].strip() == '') or (tmp[4].strip() == '') or\
                       (len(tmp1) != 4) or\
                       ((int(tmp1[0]) < 1) or int(tmp1[0]) > 254) or\
                       ((int(tmp1[1]) < 0) or int(tmp1[1]) > 254) or\
                       ((int(tmp1[2]) < 0) or int(tmp1[2]) > 254) or\
                       ((int(tmp1[3]) < 0) or (int(tmp1[3]) > 254)):
                       verifyResult = False
                       break
                except:
                    verifyResult = False
                    break
                Network_Data.append(tmp)
            if verifyResult == False:
                lblResult.configure(text='Verification Result: Failed',
                                                            foreground='red')
                tabs.tab(1,state='normal')
            else:
                lblResult.configure(text='Verification Result: Success',
                                                            foreground='green')
                tabs.tab(1,state='normal')
                btn_LoadTemplate.config(state='normal')
            cmbNetData['values']=()
            tmpcontainer=[]
            Network_Data.sort()
            for i in Network_Data:
                tmpcontainer.append(i[0]+'•••'+i[1])
            cmbNetData['values']=tuple(tmpcontainer)
    except FileNotFoundError:
        tk.messagebox.showerror('Error','File not found!')
    except PermissionError:
        tk.messagebox.showerror('Error','The address contains something but its\
                                not accessible due to the lack of permission!')
#   ____________________________txtPath on Change Function _____________________
def txtPathOnChange(event):
    if txtPath.get('1.0','end-1c') != r'Enter the file path(ex: c:/data.csv)':
        if txtPath.get('1.0','end-1c') != '':
            btnVerify.configure(state='normal')
        else:
            btnVerify.configure(state='disabled')
    else:
        btnVerify.configure(state='disabled')
#   __________________________ txtPath On Click Function _______________________
def txtPathOnClick(event):
    if txtPath.get('1.0','end-1c') == r'Enter the file path(ex: c:/data.csv)':
        txtPath.delete('1.0', "end")
        txtPath.configure(foreground='black')
#   __________________________ txtPortAdd On Click Function ____________________
def txtPortAddOnClick(event):
    if txtPortAdd.get("1.0","end-1c") == r'ex: 1/4/28':
        txtPortAdd.delete('1.0', "end")
        txtPortAdd.configure(foreground='black')
#   __________________________txtPortAdd On Change Function ____________________
def txtPortAddOnChange(event):
    if txtPortAdd.get("1.0","end-1c") != (r'ex: 1/4/28'):
        Verify = PortFormatVerify(txtPortAdd.get("1.0","end-1c"))
        if Verify == 'valid':
            txtPortAdd.configure(background='white')
        else:
            txtPortAdd.configure(background='Red')
#   ____________________________txtPortAdd on FocusOut Function ________________
def txtPortAddOnFocusout(event):
    if txtPortAdd.get("1.0","end-1c") == '':
        txtPortAdd.configure(background='white',foreground='gray')
        txtPortAdd.insert('1.0',r'ex: 1/4/28')
#   ___________________________txtPath On FocusOut Function ____________________
def txtPathOnFocusOut(event):
    if txtPath.get("1.0","end-1c") == '':
        txtPath.insert('1.0',r'Enter the file path(ex: c:/data.csv)')
        txtPath.configure(background='white',foreground='gray')
        btnVerify.configure(state='disabled')
#__________________________________ Template Load File__________________________
def loadTemplatefile():
    global Templates
    added_Templates = 0
    failed_IPs_message = ''
    failed_IPs = []
    tempOBJ = {}
    currntTemplateNames = []
    OBJ = None
    IP_List = [i[1] for i in Network_Data]
    if len(Templates) > 0:
        for i in Templates:
            currntTemplateNames.append(i.name)
    filepath = tk.filedialog.askopenfilename(initialdir='C:\\',
    title = "Select file",filetypes = (("tmplfile files","*.TMPLFILE"),
                                                    ("all files","*.*")))
    if filepath not in [None,'']:
        with open(filepath,'r') as templatefile:
            content = templatefile.read().splitlines()
        for i in content:
            failed_IPs = []
            tempOBJ = literal_eval(i)
            OBJ = Template_Builder()
            for j in tempOBJ['ports']:
                if j not in IP_List:
                    failed_IPs_message += (str(j) + ' was not included in Network Data file.\n')
                    failed_IPs.append(j)
            if len(failed_IPs) > 0:
                failed_IPs_message += ('Mismatch exists between the imported \
template and network data file.\nThe file cannot be imported!')
                tk.messagebox.showerror('Invalid nodes',failed_IPs_message)
                return
            OBJ.name = tempOBJ['name']
            OBJ.ports = tempOBJ['ports']
            OBJ.events = tempOBJ['events']
            OBJ.Commands = tempOBJ['Commands']
            if OBJ.name in currntTemplateNames:
                continue
            else:
                Templates.append(OBJ)
                added_Templates += 1
        if failed_IPs_message != '':
            tk.messagebox.showinfo('Node info mismatch',failed_IPs_message)
        tk.messagebox.showinfo('Template loading result',str(added_Templates)+
                               ' new templates have been added')
        tabs.tab(1,state='normal')
        tabs.tab(2,state='normal')
        tmplist = []
        if len(Templates) > 0:
            cmbTemplateList['values'] = ()
            for i in Templates:
                tmplist.append(i.name)
        cmbTemplateList['values'] = tuple(tmplist)
#__________________________________ Template Save Func _________________________
def Export_Temp():
    template_item = {}
    global Templates
    if len(Templates) == 0:
        tk.messagebox.showerror('Error','The template database is empty.')
        return
    filename = tk.filedialog.asksaveasfile(mode='w',defaultextension=".tmplfile",
            filetypes = (("Template files","*.tmplfile"),("all files","*.*")))
    if filename not in [None,'']:
        for i in Templates:
            template_item['name']=i.name
            template_item['ports']=i.ports
            template_item['Commands']=i.Commands
            template_item['events']=i.events
            filename.write(str(template_item))
            filename.write('\n')
        filename.close()
#__________________________________ TRAL FUNCS _________________________________
def Trial(root):
    sec = 0
    while sec < 180:
        sleep(1)
        sec += 1
    root.destroy()
#__________________________________ TRAL FUNCS _________________________________
def GoOnTrial():
    process = Process(Trial(root))
    process.start()
#__________________________________ TRAL FUNCS _________________________________
def PassCheck():
    global isTrial
    password_db = ('b09de2727f72ec243f846baafcfd380d',
                   '0f024f9bc6c8343526cea4b652baf73b',
                   '96aabcd6f2a75c05c73d16c1cfa99106',
                   '6632123f0f5a8dcf266f9c007f39ceb8',
                   'fd43104a480f535a06fbdf8e709f08be',
                   '49e5e34a2291174272af1e3791d3d2dc',
                   'deb84787a5075db49859ebd2a642ddb0',
                   '74d8afd340de7494870259fc4fe8ef39')
    hexed = md5((txtPasswd.get()).encode('ascii'))
    if hexed.hexdigest() in password_db:
        isTrial = False
        passwd_UI.destroy()
    else:
        tk.messagebox.showerror('Wrong password','Wrong password!')
#___________________________________ Time Trial Func ___________________________
def Trialer():
    global isTrial
    isTrial = True
    passwd_UI.destroy()
#__________________________________Main Part____________________________________
if __name__ == '__main__':
    freeze_support()
    passwd_UI = tk.Tk()
    passwd_UI.title('License Key Manager')
    passwd_UI.geometry('400x50')
    passwd_UI.resizable(0,0)
    ttk.Label(passwd_UI,text='Key: ',foreground='Blue').grid(column=0,
                                            row=0,padx=5,sticky='WN',pady=10)
    txtPasswd = ttk.Entry(passwd_UI , width=20,foreground='red',show="*")
    txtPasswd.grid(column=1,row=0,sticky='w',padx=5,pady=10)
    btnFull = ttk.Button(passwd_UI,text='Check',command=PassCheck)
    btnFull.grid(column=2,row=0,sticky='w',padx=5,pady=10)
    ttk.Button(passwd_UI,text='3 Minutes Trial',command=Trialer).grid(column=3,
                                                row=0,sticky='w',padx=5,pady=10)
    passwd_UI.protocol("WM_DELETE_WINDOW", exit)
    passwd_UI.bind('<Return>', lambda f2:btnFull.invoke())
    passwd_UI.mainloop()
    root = tk.Tk()
    root.title('NOKIA 1830 PSS SWDM Performance Collection Tool - Release ' + str(_version_)+' - BETA')
#____________________TrialStart_________________________________________________
    if isTrial == True:
        Thread(target=GoOnTrial).start()
#____________________TrialEnd___________________________________________________
    try:
        root.call('wm','iconphoto', root._w, tk.PhotoImage(file='NLogo.png'))
    except:
        print('NLogo.png file not found! This message can be ignored...\n')
    root.geometry('750x450')
    root.resizable(0,0)
    log_Folder = 'logs'
    try:
        mkdir(log_Folder)
    except:
        pass
#   _____________________________________ Tabs Configurations __________________
    tabs = ttk.Notebook(root)
    tab1 = tk.Frame(tabs , height=422 , width=744)
    tab2 = tk.Frame(tabs , height=422 , width=744)
    tab3 = tk.Frame(tabs , height=422 , width=744)
    tabs.add(tab1 , text='Network Data File')
    tabs.add(tab2 , text='Performance Template' , state='normal')
    tabs.add(tab3 , text='Performance Collector' , state='normal')
    tabs.grid(column=0,row=0)
#___________________________ Tab1 Label Frames Configurations __________________
    lblFrame1 = ttk.LabelFrame(tab1 , width=730, height=237 ,
                                      text='Import network data file')
    lblFrame1.grid(columnspan=4,sticky='WE',padx=5)
    lblFrame2 = ttk.LabelFrame(tab1 , width=730, height=300 ,text='About')
    lblFrame2.grid(columnspan=4,sticky='WE',padx=5)
#____________________________Tab1 Button Configurations_________________________
    btnBrowse = ttk.Button(lblFrame1 , width=10 , text='Browse...' ,
                                                        command=btnBrowseCall)
    btnBrowse.grid(column=0,row=0,padx=10,pady=5)
    btnVerify = ttk.Button(lblFrame1 , width=10 , text='Verify' ,
                                    command=btnVerifyCall , state='disabled')
    btnVerify.grid(column=0,row=1,padx=10,pady=5)

    btn_LoadTemplate = ttk.Button(lblFrame1 , width=10 , text='Load Templates',
                                    state='disabled',command=loadTemplatefile)
    btn_LoadTemplate.grid(column=0,row=2,padx=10,pady=5)
#____________________________Tab1 textbox Configurations________________________
    txtPath = CustomText(lblFrame1 , width=70 ,height=1,foreground='gray')
    txtPath.insert('1.0',r'Enter the file path(ex: c:/data.csv)')
    txtPath.grid(column=1,row=0,sticky='w',columnspan=3,padx=(32,0))
    txtPath.bind('<Button-1>', txtPathOnClick)
    txtPath.bind('<<CursorChange>>', txtPathOnChange)
    txtPath.bind('<FocusOut>', txtPathOnFocusOut)
#____________________________Tab1 Label Configurations__________________________
    lblResult = ttk.Label(lblFrame1,text='Verification Result: TBD',width = 70)
    lblResult.configure(foreground='blue')
    lblResult.grid(column=1,row=1,padx=(30,10),pady=5,sticky='W')
#_______________________Explanations____________________________________________
    ttk.Label(lblFrame2,text=' - Used 3rd-Party Libraries:',
              foreground='Blue').grid(column=0,row=0,padx=(0,100),sticky='WN')
    lblLicitem1 = ttk.Label(lblFrame2,text=' - tkintertable',foreground='Blue',
                                                                cursor="spider")
    lblLicitem1.grid(column=0,row=1,padx=(10,100),sticky='WN')
    url1 = r"https://github.com/dmnfarrell/tkintertable"
    lblLicitem1.bind('<Button-1>', lambda f: open_new(url1))
    ttk.Label(lblFrame2,text='-' * 126,
              foreground='Gray').grid(column=0,row=2,sticky='WN')
    ttk.Label(lblFrame2,text=' - Important Points:',
              foreground='Blue').grid(column=0,row=3,padx=(0,100),sticky='WN')
    ttk.Label(lblFrame2,text=' - Legacy OCS Shelves \
(PSS36/PSS64) are not supported.',foreground='Blue').grid(column=0,row=4,
                                                    padx=(10,100),sticky='WN')
    ttk.Label(lblFrame2,text=' - Feel free to contact me in case of any \
suggestions or bug reports.',foreground='Blue').grid(column=0,row=5,
                                                     padx=(10,100),sticky='WN')
#_____________________________Author____________________________________________
    lblAuthor = ttk.Label(lblFrame2,
        text='Created by Naseredin Aramnejad (naseredin.aramnejad@nokia.com)',
                                            foreground='Red',cursor='exchange')
    lblAuthor.grid(column=0,row=10,padx=(0,367),pady=(150,3),sticky='WS')
    email = r"MAILTO:naseredin.aramnejad@nokia.com"
    lblAuthor.bind('<Button-1>', lambda f1:open_new(email))
#______________________________ Tab2 Label Frames Configurations _______________
    lblFrame3 = ttk.LabelFrame(tab2 , width=730, height=120 ,text='Ports')
    lblFrame3.grid(columnspan=4,sticky='WE',padx=7)
    lblFrame4 = ttk.LabelFrame(tab2 , width=730, height=120 ,text='Events')
    lblFrame4.grid(columnspan=10,sticky='wes',padx=5,column=0,row=1)
#_______________________________Tab2 Button Configurations______________________
    pbar1 = Rotbar(parent=lblFrame3,column=2,row=3,padx=(0,5),sticky1='nw',
                  aspect=2,
                  file=r'D:\userdata\aramneja\Desktop\ezgif-5-cd5b298d317e.gif')
    pbar2 = Rotbar(parent=lblFrame3,column=2,row=4,padx=(0,5),sticky1='nw',
                  aspect=2,
                  file=r'D:\userdata\aramneja\Desktop\ezgif-5-cd5b298d317e.gif')

    ttk.Button(lblFrame3,text='Save Template',
               command=NewTemplate).grid(column=1,row=6,pady=5,sticky='nw',
                                         columnspan=4,ipadx=27,ipady=25)
    btnLoadCard = ttk.Button(lblFrame3,text='...',
    command=lambda :Proc_Pbar(pbar1,LoadCards),width=2,state='disabled')
    btnLoadCard.grid(column=2,row=3,padx=(0,5),sticky='nw')
    btnLoadInt = ttk.Button(lblFrame3,text='...',
    command=lambda :Proc_Pbar(pbar2,LoadInts),width=2,state='disabled')
    btnLoadInt.grid(column=2,row=4,padx=(0,5),sticky='nw')
    ttk.Button(lblFrame3,text='Add to List',command=Add2Port).grid(column=3,
                                                row=3,sticky='nw',rowspan=2)
    ttk.Button(lblFrame3,text='Remove',command=DeletePort).grid(column=3,row=4,
                                            sticky='nw',rowspan=3,pady=(0,3))
    ttk.Button(lblFrame4,text='Add to List',command=Add2Event).grid(column=1,
                row=2,padx=(0,107),sticky='nw',columnspan=2,ipadx=33,ipady=12)
    ttk.Button(lblFrame4,text='Remove',command=DeleteEvent).grid(column=1,row=3,
                        padx=(0,107),sticky='nw',columnspan=2,ipadx=33,ipady=12)
    ttk.Button(lblFrame3,text='Export Tmpl',command=Export_Temp).grid(column=2,
                        row=6,pady=5,sticky='nw',columnspan=4,ipadx=8,ipady=25)

#_______________________________Tab2 ListBox Configurations_____________________
    lstTempl = tk.Listbox(lblFrame3,width=59,height=13)
    lstTempl.grid(column=5,row=1,sticky='w',columnspan=2,rowspan=6,padx=(0,5),
    pady=(0,5))
    yscroll2 = tk.Scrollbar(lblFrame3,command=lstTempl.yview,orient='vertical')
    yscroll2.grid(column=4,row=1,sticky='wsn',padx=(5,0),rowspan=6,pady=(0,5))
    lstTempl.configure(yscrollcommand=yscroll2.set)
    lstSelectedEvents = tk.Listbox(lblFrame4,width=61,height=9)
    lstSelectedEvents.grid(column=5,row=0,sticky='wn',rowspan=5,pady=(5,10))
    yscroll4 = tk.Scrollbar(lblFrame4,command=lstSelectedEvents.yview,
                                                            orient='vertical')
    yscroll4.grid(column=4,row=0,sticky='wsn',padx=(12,0),pady=(5,10),rowspan=5)
#   _______________________Tab2 Radio Buttons Configurations____________________
    OnlineVar = tk.IntVar()
    radio_frame = ttk.Frame(lblFrame3)
    radio_frame.grid(column=2,columnspan=2,row=2)
    ttk.Radiobutton(radio_frame, text='Offline',variable=OnlineVar,value=1,
                    command=GoOffline).grid(column=0,row=0)
    ttk.Radiobutton(radio_frame, text='Online',variable=OnlineVar,value=2,
                    command=GoOnline).grid(column=1,row=0)
    OnlineVar.set(1)
#   ____________________________Tab2 ComboBos Configurations____________________
    cmbNetData = ttk.Combobox(lblFrame3,state='readonly',width=40)
    cmbNetData.grid(column=1,row=1,padx=(0,10),sticky='nw',columnspan=4)
    cmbNetData.bind('<<ComboboxSelected>>', Init_Shelfs)
    cmbShelfs= ttk.Combobox(lblFrame3,state='readonly')
    cmbShelfs.grid(column=1,row=2,sticky='nw',pady=(1,0))
    cmbShelfs['values']=('1830 PSS-8/16II/32','1830 PSS-24x','1830 PSS-8x/12x')
    cmbShelfs.bind('<<ComboboxSelected>>', ShelfOnSelect)
    cmbCards = ttk.Combobox(lblFrame3,state='readonly')
    cmbCards.grid(column=1,row=3,sticky='nw',pady=(1,0))
    cmbCards.bind('<<ComboboxSelected>>',Init_Interface)
    cmbInterfaces= ttk.Combobox(lblFrame3,state='readonly')
    cmbEventType= ttk.Combobox(lblFrame4,state='readonly')
    cmbEventType.grid(column=1,row=0,padx=(0,10),sticky='nw')
    cmbEventType['values']=('Ethernet','WDM','OSC_OPT','OSC_OPR')
    cmbEventType.bind('<<ComboboxSelected>>', cmbEventTypeOnSelect)
    cmbSelectedEvents= ttk.Combobox(lblFrame4,state='readonly')
    cmbSelectedEvents.grid(column=1,row=1,padx=(0,10),sticky='nw')
#   ____________________________Tab2 Text Box Configurations____________________
    txtPortAdd = CustomText(lblFrame3,width=17,height=1)
    txtPortAdd.grid(column=1,row=4,padx=(0,10),sticky='nw')
    txtPortAdd.insert("end", r'ex: 1/4/28')
    txtPortAdd.configure(foreground='gray')
    txtPortAdd.bind('<Button-1>', txtPortAddOnClick)
    txtPortAdd.bind('<<CursorChange>>', txtPortAddOnChange)
    txtPortAdd.bind('<FocusOut>', txtPortAddOnFocusout)
#   __________________________________ Tab2 Label Configurations _______________
    ttk.Label(lblFrame3,text='Node: ').grid(column=0,row=1,padx=(5,0),
                                            sticky='wn')
    ttk.Label(lblFrame3,text='Shelf Type: ').grid(column=0,row=2,padx=(5,0),
                                                  sticky='wn')
    ttk.Label(lblFrame3,text='Card Type: ').grid(column=0,row=3,padx=(5,0),
                                                 sticky='wn')
    ttk.Label(lblFrame3,text='Port Address: ').grid(column=0,row=4,padx=(5,0),
                                                    sticky='wn')
    ttk.Label(lblFrame4,text='Event Type: ').grid(column=0,row=0,padx=(5,0),
                                                  sticky='wn')
    ttk.Label(lblFrame4,text='Event Name: ').grid(column=0,row=1,padx=(5,0),
                                                  sticky='wn')
#   _____________________________ Tab3 Label Frame Configuration _______________
    lblFrame5 = ttk.LabelFrame(tab3 , width=735, height=120 ,text='Collector')
    lblFrame5.grid(columnspan=10,sticky='wes',padx=5,column=0,row=0)
    lblFrame6 = ttk.LabelFrame(tab3 , width=735, height=334 ,text='Result')
    lblFrame6.grid(columnspan=10,sticky='wes',padx=5,column=0,row=1)
    Frame1 = ttk.Frame(lblFrame5 , width=300, height=50)
    Frame1.grid(columnspan=2,sticky='wes',padx=5,column=2,row=1)
#   _____________________________ Tab3 Label Configuration _____________________
    ttk.Label(lblFrame5,text='Templates List: ').grid(row=0,column=0,padx=5,
                                                      pady=5,sticky='nw')
    ttk.Label(lblFrame5,text='Collection Process Quantity: ').grid(row=1,
                                column=0,padx=5,pady=5,sticky='ne',columnspan=2)
    ttk.Label(lblFrame5,text='Collection Status: ').grid(row=1,column=4,padx=5,
                                                         pady=5,sticky='nw')
    lblCollectionStatusResult = ttk.Label(lblFrame5,text='TBD')
    lblCollectionStatusResult.grid(row=1,column=5,padx=5,pady=5,sticky='nw',
                                   columnspan=3)
    ttk.Label(Frame1,text='1').grid(row=0,column=0,padx=3)
    ttk.Label(Frame1,text='100').grid(row=0,column=2,padx=3)
    ttk.Label(lblFrame5,text='Process Qty: ').grid(row=0,column=4)
    lblCurrentPrQtyValue = ttk.Label(lblFrame5,text='1')
    lblCurrentPrQtyValue.grid(row=0,column=5)
#   _____________________________ Tab3 Button & Pbar Configuration _____________
    progressVar = tk.DoubleVar()
    progress = ttk.Progressbar(lblFrame5,orient='horizontal',length=250,
                 variable=progressVar,mode='determinate',maximum=1001,value=0)
    progress.grid(row=0,column=3,padx=5,pady=5,columnspan=2,sticky='wn')
    pbar3 = Rotbar(parent=lblFrame5,row=0,column=2,sticky1='wn',
                   padx=5,pady=5,columnspan=2,aspect=2,
                  file=r'D:\userdata\aramneja\Desktop\ezgif-5-cd5b298d317e.gif')
    btnExecute = ttk.Button(lblFrame5,text='Collect',
                            command=lambda :Proc_Pbar(pbar3,Collector))
    btnExecute.grid(row=0,column=2,sticky='wn',padx=5,pady=5,columnspan=2)
    btnExport = ttk.Button(lblFrame5,text='Exp',command=TableExport,
                           state='disabled')
    btnExport.configure(width=5)
    btnExport.grid(row=0,column=6,sticky='wn',pady=5)
    scaleVal = tk.DoubleVar()
    scaleVal.set(1.0)
    scale = ttk.Scale(Frame1,orient='horizontal',length=200,variable=scaleVal,
                      from_=1,to=100,command=updateValue)
    scale.grid(row=0,column=1,padx=5,pady=5,sticky='wn')
#   _____________________________ Tab3 Combobox Configuration __________________
    cmbTemplateListVar = tk.StringVar()
    cmbTemplateList = ttk.Combobox(lblFrame5,textvariable=cmbTemplateListVar,
                                   state='readonly')
    cmbTemplateList.grid(row=0,column=1,padx=5,pady=5,sticky='wn')
    fdata = {1:{'Port':0,'Event 1':0}}
    table = TableCanvas(lblFrame6, data=fdata,width=670,height=273).show()
#   _____________________________________ Main Loop Execution __________________
    root.mainloop()
