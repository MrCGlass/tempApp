import wx,socket,asyncio
import threading,os,json,sqlite3 as sql
from kmip import KmipClient
from OpenSSL import crypto

## Main widget Screen (needs update) ###

class keyClient(KmipClient):
    def __init__(self,*args,**kwargs):
        super(keyClient,self).__init__(*args,**kwargs)


class mainScreen(wx.Panel):
    
    def __init__(self,*args,**kwargs):
        super(mainScreen,self).__init__(*args)
        self.setupWidgets(kwargs['server'],kwargs['parent'],kwargs['socket'])
        self.infobox.Add(self.label,1,wx.EXPAND)
        self.buttonbox.Add(self.serverButton,1,wx.EXPAND)
        self.buttonbox.Add(self.stopServer,1,wx.EXPAND)
        self.infobox.Add(self.buttonbox,1,wx.EXPAND)
        self.container.Add(self.infobox,1,wx.EXPAND)
        self.container.Add(self.logger,1,wx.EXPAND)
        self.SetSizerAndFit(self.container)
        
    # widget setup #
    def setupWidgets(self,server,parent,socket):
        self.container = wx.BoxSizer(orient= wx.HORIZONTAL)
        self.infobox = wx.BoxSizer(orient= wx.VERTICAL)
        self.buttonbox = wx.BoxSizer(orient= wx.HORIZONTAL)
        self.logger = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.label = wx.StaticText(self, label='hello world')
        self.serverButton = wx.Button(self,label='start')
        self.stopServer = wx.Button(self,label='stop')
        self.serverButton.Bind(wx.EVT_BUTTON,handler=lambda x: server(socket))
        self.stopServer.Bind(wx.EVT_BUTTON,handler=parent.stopServer)

## root window ##
class mainwindow(wx.Frame):
    config_path=os.getcwd() +'/configfiles/server.conf',
    con = sql.Connection('appdata.db')
    cursor = con.cursor()
    
        
    def __init__(self,*args,**kwargs):
        super(mainwindow,self).__init__(*args,**kwargs)

        
        self.create_base(self.cursor)
        host = socket.gethostbyname(socket.gethostname())
        
        port = 7000
        
        s = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
        
        s.bind((host,port))
        self.numberofusers = 0
        s.listen(1)
        self.serverThread = self.startServer
        self.connectionThread = threading.Thread(target=self.new_connection, args=(s,))
        self.tLock = threading.Lock()
        self.screen = mainScreen(self,parent=self,server=self.serverThread,socket=s)
        self.SetClientSize(self.screen.GetBestSize())
        self.connected = True
        self.userlist = []
        self.usernumber = {}
        
        self.Update()

        self.keyclient = keyClient(
            username='appserver',
            password='collective',
            config_file=os.getcwd() +'/configfiles/client.conf'
            )
   
    # start server threads #
    def startServer(self, s):

        self.connectionThread.start()
        

    # create initial database #
        
    def create_base(self,cursor):
        cursor.execute("CREATE TABLE IF NOT EXISTS members(firstname TEXT, lastname TEXT,\
                        username TEXT, password TEXT, email TEXT, job TEXT, phone REAL,\
                       city TEXT, state TEXT, photo BLOB)")
        
        cursor.execute('CREATE TABLE IF NOT EXISTS jobs(name TEXT, location TEXT, category TEXT,\
                        description TEXT, manager TEXT, city TEXT, state TEXT, photos BLOB)')

    
    # listen for new device connections #
    def new_connection(self,s):
          while self.connected:
            try:
                # add device to users list #
                
                c,addr = s.accept()
                self.screen.logger.AppendText('Connection from: {}, {} \n'.format(str(addr),str(c)))
                messageThread = threading.Thread(target=self.user_messages,args=(c,addr))
                messageThread.start()
                self.usernumber[c]=self.numberofusers
                self.userlist.append((c,messageThread))
                self.numberofusers +=1
                
               
            except Exception as e:
                self.screen.logger.AppendText(str(e))
            else:
                pass
    # get messages from users #
    def user_messages(self,s,addr):
        while self.connected:
            try:

                # get message #
                
                data = s.recv(1000000)
                self.tLock.acquire()
                self.screen.logger.AppendText('request from {}: {} \n'.format(addr,data.decode()))
                data = data.decode()
        
                data = json.loads(data)

                    # handle log In request #
                if data['tag'] == 'logIn':
                    self.screen.logger.AppendText('User {}: requests login \n'.format(data['username']))
                    s.send(self.getlogin(data))

                    # handle new user requset#
                if data['tag'] == 'createNewUser':
                    self.screen.logger.AppendText('User {}: requests to be a member \n'.format(data['username']))                              
                    s.send(self.create_new_user(data))

                    # handle job searcch request #
                if data['tag'] == 'search_request':
                    self.screen.logger.AppendText('User {}: requests for jobs \n'.format(data['username']))         
                    s.send(self.get_search(data))

                    # handle new job request #
                if data['tag'] == 'newjob':
                    self.screen.logger.AppendText('user {}:created a new job \n'.format(data['manager']))
                    s.send(self.new_job(data))

                    # handle user job request 
                if data['tag'] == 'myjobs':
                    self.screen.logger.AppendText('user {}: requests presonal jobs \n'.format(data['username']))
                    s.send(self.get_user_jobs(data))
                    
                    # all category request #
                    if data['tag'] == 'getCategorie':
                        self.screen.logger.AppendText('user {}: requests all categories\n'.format(data['username']))
                        user[0].send(self.get_category(data))
                    # user job edit #
                    if data['tag'] == 'editjob':
                        self.screen.logger.AppendText('user {}: request job edit\n'.format(data['jobinfo']['manager']))
                        user[0].send(self.get_job_edit(data['jobinfo']))
                        

                if data['tag'] == 'getCategorie':
                    self.screen.logger.AppendText('user {}: requests all categories\n'.format(data['username']))
                    s.send(self.get_category(data))

                if data['tag'] == 'editjob':
                    self.screen.logger.AppendText('user {}: request job edit\n'.format(data['jobinfo']['manager']))
                    s.send(self.get_job_edit(data['jobinfo']))

                        
                        
                  
            except Exception as e:
                    
                self.userlist.pop(self.usernumber[s])
                if self.numberofusers > 1:
                    self.numberofusers -= 1
                print(e,1)

            finally:
                    self.tLock.release()

    # handle job search #
    def get_search(self,data):
        con = sql.Connection('appdata.db')
        cursor = con.cursor()
        try:
            cursor.execute('SELECT * FROM jobs WHERE category=?',(data['search'],))
            jobs = cursor.fetchall()
            if not jobs:
                message = {'tag':'message',2:'No {} category found'.format(data['search']),'status':False}
            else:
                message = {'tag':'search', 2:'{} Jobs'.format(data['search']),'category': jobs}
           
            
            
        except Exception as e:
            message = {'tag':'message',2:'No {} catagory found'.format(data['search']), 'category': False}
            print(e,6)
            

        finally:
            
            cursor.close()
            con.close()
            message = json.dumps(message)
            return message.encode()

    # new user handler #
    def create_new_user(self,data):
        con = sql.Connection('appdata.db')
        cursor = con.cursor()
        

        try:
            
            cursor.execute('INSERT INTO members (firstname,lastname,username,password,email,phone,city,state,photo) VALUES (?,?,?,?,?,?,?,?,?)',
                           (data['firstname'],data['lastname'],data['username'],
                            data['password'],data['email'],data['phone'],data['usercity'],
                            data['userstate'],str(data['userimage'])))
            con.commit()
            message = {'tag':'message', 2: 'New Member added','status':'newuser' }

        except Exception as e:
            message = {'tag':'message', 2:'Error creating member' ,'status':'fail'}
            print(e,3)

        finally:
            cursor.close()
            con.close()
            message = json.dumps(message)
            message = message.encode()
            return message

    # user log in handler #
    def getlogin(self,data):
        con = sql.Connection('appdata.db')
        cursor = con.cursor()
        message = None
        try:
            
            cursor.execute('SELECT * FROM members where username == ?', (data['username'],))
            names = cursor.fetchall()
          
            
            for name in names:
                if name[3] == data['password']:
                    message = {'tag':'message', 2: 'Welcome {}'.format(data['username']), 'status':'pass','account':name}
                
                    break

                else:
                    message = {'tag':'message', 2: 'incorrect password', 'status':'fail'}
                 
        
        except Exception as e:
            message = {'tag':'message' ,2:'No user by that Name', 'status':'fail'}
            
            print(e,4)

        finally:
            if not message:
                message = {'tag':'message', 2:'No user by that Name'}
               
            cursor.close()
            con.close()
            message = json.dumps(message)
            message = message.encode()
            return message
        
    # user new job handler #
    def new_job(self,data):
        con = sql.connect('appdata.db')
        cursor = con.cursor()
        self.screen.logger.AppendText('{} \n'.format(data))
        try :
            cursor.execute("INSERT INTO jobs (name,category,description,location,manager,state,city) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (data['name'],data['category'],data['description'],data['location'],data['manager'],data['state'],data['city']))

            cursor.execute('Select * from jobs WHERE manager = ?',(data['manager']))

            job = cursor.fetchall()
            
           
            cursor.execute("UPDATE members SET job = ? WHERE username == ?",(json.dumps(job),data['manager']))
            con.commit()
            message = { 'tag':'message', 2:'Job Created','status': 'created' }
            
        except Exception as e:
            
            message = {'tag':'message',2:'Error Creating Job','status':'fail'}
            print(e,2)

        finally:
            
            if not message:
                message = {'tag':'message',2:'Error Creating Job','status':'fail'}
            cursor.close()
            con.close()
            message = json.dumps(message)
            return message.encode()
        
    # get user jobs handler #
    def get_user_jobs(self,data):
        con = sql.connect('appdata.db')
        cursor = con.cursor()
        try:
            cursor.execute('SELECT * FROM jobs WHERE manager = ?',(data['username']))
            jobs = cursor.fetchall()
            message = {'tag':'search','category':jobs,2: 'Personal Jobs'}
                

        except Exception as e:
            message = {'tag':'message',2:'error finding jobs'}
            print(e)

        finally:
            cursor.close()
            con.close()
            message = json.dumps(message)
            return message.encode()
        
    # all category search handler #
    def get_category(self,data):

        con =sql.connect('appdata.db')
        cursor = con.cursor()

        try:
            cursor.execute('SELECT * FROM jobs WHERE category = ? AND manager != ?',(data['category'],data['username']))
            jobs = cursor.fetchall()
            message = {'tag': 'search','category':jobs, 2: 'All Categories'}

        except Exception as e:
            message = {'tag':'message',2:'error retrieving jobs'}
            print(e)
        finally:
            cursor.close()
            con.close()
            message = json.dumps(message)
            return message.encode()
        
    # handle user job edit #
    def get_job_edit(self,data):

        con = sql.connect('appdata.db')
        cursor = con.cursor()

        try:
            cursor.execute('UPDATE Jobs SET name = ?, category = ?, location = ?, city = ?, state = ?, description = ?\
                           WHERE manager == ? and name == ? ' , (data['newname'], data['category'],data['location'],
                                                                 data['city'],data['state'],
                                                                data['description'],data['manager'],data['oldname']))

            

            cursor.execute('SELECT * from jobs where manager == ?',(data['manager'],))
            jobs = cursor.fetchall()

            cursor.execute('UPDATE members set job = ? WHERE username == ?',(json.dumps(jobs),data['manager']))
            con.commit()
            message = {'tag': 'jobedit', 2: 'Edit Successful', 'status': 'pass'}
        except Exception as e:
            message = {'tag': 'message',2: 'error editing job','status': 'fail'}
            print(e)

        finally:
            cursor.close()
            con.close()
            message = json.dumps(message)
            return message.encode()
    # server stop handler( needs update) #
    def stopServer(self,event):
        self.connected = False
        self.keyclient.open()
        print('false')


async def main():
    app = wx.App()
    window = mainwindow(None,wx.ID_ANY,
                        size=(900,600))
    window.Show(True)

    app.MainLoop()
    
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
    
            
