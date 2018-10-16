from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.listview import ListItemButton
from kivy.network.urlrequest import UrlRequest
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.core.image import Image as im
from kivy.uix.image import AsyncImage as Image
from kivy.factory import Factory
from kivy.graphics import Rectangle,Ellipse,Color
from PIL import Image as pimage
from kivy.clock import Clock
import socket,threading,os
import json,io


## Job Creation page ##
class JobCreatePage(BoxLayout):
    categoryList = ['Lawn','Technolog','Handyman','Cleaning','Home Care']
    info_label = ObjectProperty()
    mainbutton = ObjectProperty()
    def __init__(self,*args,**kwargs):
        super(JobCreatePage,self).__init__()
        method = args[0]
        dropdown = DropDown()
        
        for cat in self.categoryList:
            btn = Button(text=cat,size_hint_y=None,height=44)
            btn.bind(on_release=lambda btn:dropdown.select(btn.text))\
            dropdown.add_widget(btn)
            
        self.mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance,x:setattr(self.mainbutton,'text',x))
        
        if method == 'edit':
            self.header.text = 'Edit Job'
            self.submit_button.text = 'Submit Edit'
            

        
## Job Display Page ##
class ShowJobPage(BoxLayout):
    button_panel = ObjectProperty()
    editbutton = ObjectProperty()
    def __init__(self,*args,**kwargs):
          super(ShowJobPage,self).__init__(*args,**kwargs)

    # get job map info #
    def get_display(self):
        app_id = 'j0qyg2HfhEX4NBgOwXW0'
        app_code = 'uQPNqNV9lEuioDXUP4ybDg'
        
        map_template = 'https://image.maps.api.here.com/mia/1.6/ mapview?app_id={}&app_code={}&ci={}'.format(app_id,app_code,self.location_text.text)
        request = UrlRequest(map_template,self.display_map)
          
        if self.parent.user_name == self.job[4]:
            self.editbutton = Button(text='Edit')
            self.editbutton.bind(on_press=self.parent.getPress)
            self.button_panel.add_widget(self.editbutton)
               
    # display job location map #
    def display_map(self,request,data):
        
        data = io.BytesIO(data)
          
        self.image = im(data,ext='png')
        with self.info_layout.canvas:
            Rectangle(texture=self.image.texture,
                      size=(self.image.width,self.image.height),
                      pos=(250,50))

## Search Display Screen ##             
class SearchScreen(BoxLayout):
      
    data_item = ListProperty()
    
    # convert list item button data #
    def args_converter(self,index,data_item):
        if isinstance(data_item,list):
            job = data_item[0]
        else:
            job = data_item
        self.data_item = data_item
        return {'jobs':job,'data_item':self.data_item}
    


        
## Job search list Buttons ##
class JobListbutton(ListItemButton):
    jobs = StringProperty()
    data_item = ListProperty()

# User Profile Image Container ##
class Imagephoto(BoxLayout):
    texture= ObjectProperty()
    def __init__(self,*args,**kwargs):
        super(Imagephoto,self).__init__()
        with self.canvas:
            Color(1,1,0)
        
## User Profile Image ## 
class userphoto(Imagephoto):

    # Image setup #
    def setup(self,data):
        try:
            data = io.BytesIO(data)
            self.image = im(data,ext='jpg')
            photo = Rectangle(texture=self.image.texture,
                              size=self.image.size,
                              pos=(self.x+30,360))
            self.canvas.before.add(photo)
            self.canvas.ask_update()
        except Exception as e:
            print(e)
        finally:
            pass
            
        return
    
        
## Account Page Display ##
class AccountPage(BoxLayout):
    search_button=ObjectProperty()
    exit_button = ObjectProperty()
    job_button = ObjectProperty()
    my_jobButton = ObjectProperty()
    image_source = ListProperty()
    user_image = ObjectProperty()
    
    
    def __init__(self,*args,**kwargs):
        super(AccountPage,self).__init__()
        
        self.data = bytes(json.loads(args[0]['account'][9]))
        Clock.schedule_once(self.setup_photo,.21)

    ## User Profile Image Call ##
    def setup_photo(self,dt):
        
        photo_widget = userphoto()
        self.user_image.clear_widgets()
        photo_widget.setup(self.data)
        self.user_image.add_widget(photo_widget)
        return

## New User Creation Page ##
class CreateLogWindow(BoxLayout):
    info_label = ObjectProperty()
    phone = ObjectProperty()
    name_input = ObjectProperty()
    phone_input = ObjectProperty()
    pass_input = ObjectProperty()
    confirm_pass = ObjectProperty()
    email = ObjectProperty()
    state_input = ObjectProperty()
    city_input = ObjectProperty()
    first_nameInput = ObjectProperty()
    lasst_nameInput = ObjectProperty()
    file_text = StringProperty()
    photo_file = ListProperty()
   
    
    
    def __init__(self,*args,**kwargs):
        super(CreateLogWindow,self).__init__(*args,**kwargs)

    # Get New User Profile Image#
    def load_photo(self,path,filename):
        if len(filename):
            try:
                with open(os.path.join(path,filename[0]),'rb') as data:
                    self.file_text = str(data.name)
                    image = Image(source=os.path.join(path,filename[0]))
                  
                    self.photo_file = data.read()
                    
            except Exception as e: 
                print(e)
            finally:
                    pass
        return

        
##  Initial Window ##             
class MainWindow(BoxLayout):
    
    def __init__(self,*args,**kwargs):
        super(MainWindow,self).__init__(*args,**kwargs)    

## User Login In Window ##                 
class LoginWindow(BoxLayout):
    info_label = ObjectProperty()
    name_input = ObjectProperty()
    pass_input = ObjectProperty()
    def __init__(self,*args,**kwargs):
        super(LoginWindow,self).__init__(*args, **kwargs)

## Root Window ##
class mainRoot(BoxLayout):

    orientation = 'verticle'
    
    sock = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
    
    main_window = ObjectProperty()
    create_login = ObjectProperty()
    account_page = ObjectProperty()
    login_window = ObjectProperty()
    search_screen = ObjectProperty()
    job_create = ObjectProperty()
    job_page = ObjectProperty()
    old_page = ObjectProperty()
    user_data = ObjectProperty()
    jobinfo = ObjectProperty()
    
    first_name = StringProperty()
    last_name = StringProperty()
    user_name = StringProperty()
    user_pass = StringProperty()
    userstate = StringProperty()
    usercity = StringProperty()
    user_email = StringProperty()
    user_search = StringProperty()
    jobname = StringProperty()
    job_descript = StringProperty()
    job_location = StringProperty()
    job_category = StringProperty()
    
    image_source = ListProperty()
    user_jobs = ListProperty()

    user_phone = NumericProperty()
    
    categoryList = ['Lawn','Technolog','Handyman','Maid','Baby Sitter']

    def __init__(self,*args,**kwargs):
        super(mainRoot,self).__init__(*args,**kwargs)
        self.connected = False
        self.messageThread = threading.Thread(target=self.get_messages)
        self.get_connected()

    #  Main Button Imput handler #
    def getPress(self,*args,**kwargs):

        # create new user #
        if args[0].text == 'Create New':
            self.create_login = CreateLogWindow()
            self.clear_widgets()
            self.add_widget(self.create_login)
            return

        # User Login #
        elif args[0].text == "Log in":
            self.clear_widgets()
            self.login_window = LoginWindow()
            self.add_widget(self.login_window)
            return

        # Sumit new user info #
        elif args[0].text == 'Submit':
            self.user_name = self.create_login.name_input.text
            self.user_pass = self.create_login.pass_input.text
            self.confirm = self.create_login.confirm_pass.text
            self.user_email = self.create_login.email.text
            self.user_phone = self.create_login.phone.text
            self.userstate = self.create_login.state_input.text
            self.usercity = self.create_login.city_input.text
            self.first_name,self.last_name = self.create_login.first_nameInput.text,self.create_login.last_nameinput.text
            self.image_source = [x for x in self.create_login.photo_file] if len(self.create_login.photo_file) else []
            for x in [self.user_name,self.first_name,self.last_name,self.user_phone,
                      self.user_pass,self.confirm,self.user_email]:
                if   x == '':
                    self.create_login.info_label.text ='please enter a valid entry'
                    return
                
                if self.user_pass != self.confirm:
                    self.create_login.info_label.text = 'Passwords do not match'
                    return
                
            data = {'firstname':self.first_name,'lastname':self.last_name, 'username':self.user_name,
                    'password':self.user_pass,'tag':'createNewUser','email':self.user_email,
                    'usercity':self.usercity,'userstate':self.userstate,'phone':self.user_phone,'userimage':self.image_source}
            
            data = json.dumps(data)
        
            data = data.encode()
            self.sock.sendall(data)
            self.children[0].info_label.text = 'Creating User Please Wait'
            return

        # User Login #
        elif args[0].text == 'Enter':
            self.user_name = self.login_window.name_input.text
            self.user_pass = self.login_window.pass_input.text
            for x in [self.user_name, self.user_pass]:
                if x == '':
                    self.login_window.info_label.text ='please enter a valid Name and Password'
                    return
            data = {'tag':'logIn','username':self.user_name,'password':self.user_pass}
            data = json.dumps(data)
            self.sock.send(data.encode())
            self.login_window.info_label.text = "Loging In Please Wait"
            return

        # Job Search #
        elif args[0].text =='Search':
            self.user_search = self.search_screen.search_input.text
            if not self.user_search:
                 self.children[0].info_label.text = 'please enter a valid category'
                 return
            data = {'tag':'search_request', 'search': self.user_search,'username':self.user_name}
            data = json.dumps(data)
            self.sock.send(data.encode())
            return

        # Get Job create page #
        elif args[0].text =='New Job':
            self.swapwidgets(widget=args[0].text)
            return

        # Get Job Search Page #  
        elif args[0].text == 'Search Jobs':
            self.swapwidgets(widget=args[0].text)
            return

        # Submit New Job Data #
        elif args[0].text == 'Create Job':
            self.jobname = self.job_create.job_name_input.text
            self.job_descript = self.job_create.descript_input.text
            self.job_location = self.job_create.location_input.text
            self.job_category = str(self.job_create.mainbutton.text).lower()
            self.jobState = self.job_create.job_state.text
            self.jobCity = self.job_create.job_city.text

           

            for x in [self.jobname,self.jobState,self.jobCity,self.job_descript,self.job_location,self.job_category]:
                 if  x == '' or x == None:
                    self.children[0].info_label.text = 'please enter valid information'
                    return
               
            data = {'tag':'newjob', 'description':self.job_descript,'name':self.jobname,
                        'location':self.job_location, 'category':self.job_category,
                    'manager':self.user_name,'state':self.jobState,'city':self.jobCity 
                    }
            data = json.dumps(data)
            data = data.encode()
            self.sock.send(data)
            return

        # Submit Job Edit Data #        
        elif args[0].text == 'Submit Edit':
            info = self.job_setup(self.user_data)
            data = {'tag': 'edit job', 'jobinfo':info}
            data = json.dumps(data)
            data = data.encode()
            self.sock.send(data)
            return

        # Job Search List Button Handler #
        elif isinstance(args[0],ListItemButton) :
            # send category search 
            if (args[0].jobs in self.categoryList):
                category = str(args[0].jobs).lower()
                data = {'tag':'getCategorie','username':self.user_name,'category':category}
                data = json.dumps(data)
                data = data.encode()
                self.sock.send(data)
            # get job  page #
            else:
                self.swapwidgets(widget=[args,args[0]])
            return

        # Get Job Edit Page #
        elif args[0].text == 'Edit':
            self.swapwidgets(widget=args[0].text)
            return

        # get personal jobs #
        elif args[0].text == 'My Jobs':
            data = {'tag':'myjobs','username':self.user_name}
            data = json.dumps(data)
            data = data.encode()
            self.swapwidgets(widget=args[0].text)
            self.sock.send(data)
            return

        # get all categories #
        elif args[0].text == 'All Categories':
            self.search_screen.search_results.item_strings = self.categoryList
            self.search_screen.search_results.adapter.data.clear()
            self.search_screen.search_results.adapter.data.extend(self.categoryList)
            self.search_screen.search_results._trigger_reset_populate()
            self.search_screen.info_label.text = 'All Categories'
            return
                

    # handle back button #
    def pageReturn(self,page):
        self.clear_widgets()
        if page == 'login':
            new_widget = self.main_window
            
        if page == 'acctpage':
            new_widget = self.login_window
            if new_widget == None:
                new_widget = LoginWindow()
            
        if page == 'createlog':
            new_widget = self.main_window

        if page == 'searchscreen':
            new_widget = self.account_page
        if page == 'jobcreate':
            new_widget = self.account_page

        if page == 'jobpage':
            new_widget = self.oldpage
        
        self.add_widget(new_widget)
        return

    # get connection (needs update) #
    def get_connected(self):
        if self.connected == False:
            try:
                self.sock.connect(('10.0.0.83',7000))
                print('connected')
                self.connected = True
                self.messageThread.start()
            except Exception as e:
                print(e)
                self.connected = False

            else:
                pass      
        else:
            return
        
    # get server message (need update) #
    def get_messages(self):
        while self.connected:
            try:
                c = self.sock.recv(10000)
                c = c.decode()
                c = json.loads(c)
                self.handel_data(c)
              
            except Exception as e:
                self.connected = False
                print(e,1)

            finally:
                if self.connected == False:
                    self.get_connected()
                    
    # handle server messages #
    def handel_data(self,data):
        print(data)
        if data['tag'] == 'message':
            self.children[0].info_label.text = data['2']
            try:
                if data['status'] == 'pass':
                    self.clear_widgets()
                    self.account_page = AccountPage(data)
                    self.add_widget(self.account_page)

                    
                if data['status'] == 'created':
                    self.clear_widgets()
                    self.add_widget(self.account_page)

                if data['status'] == 'newuser':
                    self.logIn = LoginWindow()
                    self.clear_widgets()
                    self.logIn.info_label.text = 'User Created You Can access your account'
                    self.add_widget(self.logIn)
                if data['account']:
                    self.user_data = data
            except Exception as e:
                print(e,9)
            finally:
                pass
            
        if data['tag'] == 'search':
                self.getSearch(data)
               
        return

    # handle page swap #
    def swapwidgets(self,widget):
    
        if widget == 'Search Jobs' or 'My Job':
            self.search_screen = SearchScreen()
            self.clear_widgets()
            self.add_widget(self.search_screen)

        if widget == 'New Job':
            self.job_create = JobCreatePage('new')
            
            self.clear_widgets()
            self.add_widget(self.job_create)

        if widget == 'Edit':
            self.job_create = JobCreatePage('edit')
            self.clear_widgets()
            self.add_widget(self.job_create)
            

        if  isinstance(widget,list):
            print(widget[1].data_item)
            self.job_page = ShowJobPage()
            self.job_page.job = widget[1].data_item
            self.job_page.label_title.text = widget[1].data_item[0]
            self.job_page.descript_text.text = widget[1].data_item[3]
            self.job_page.location_text.text = '{},{}'.format(widget[1].data_item[5],widget[1].data_item[6])
            self.job_page.category_text.text = widget[1].data_item[2]
            self.oldpage = self.children[0]
            self.clear_widgets()
            self.add_widget(self.job_page)
            self.job_page.get_display()
        return

    # handles job search list #
    def getSearch(self,data):
        jobs = data['category']
        self.search_screen.search_results.item_strings = jobs
        self.search_screen.search_results.adapter.data.clear()
        self.search_screen.search_results.adapter.data.extend(jobs)
        self.search_screen.search_results._trigger_reset_populate()
        self.search_screen.info_label.text = data['2']
        return
    
    # handle job edit #
    def job_setup(self,data):
        if self.job_create.job_name_input.text != '':
            data['name'] = self.job_create.job_name.text

        if self.job_create.descript_input.text != '':
            data['description'] = self.job_create.job_description.text

        if self.job_create.location_input.text != '':
            data['location'] = self.job_create.job_description.text

        if self.job_create.mainbutton.text.lower() != 'choose':
            data['category'] = self.job_create.mainbutton.text.lower()

        if self.job_create.job_state.text != '':
            data['state'] = self.job_create.job_state.text

        if self.job_create.job_city.text != '':
            data['city'] = self.job_create.job_city.text
        print(data)
        return data

# app root #        
class simpleApp(App):
    def __init__(self,*args,**kwargs):
        super(simpleApp,self).__init__(*args,**kwargs)


if __name__ == "__main__":
  simpleApp().run()
