import requests
import urllib.request
import random 
import math
import collections
import matplotlib.pyplot as plt
import numpy as np
import passkey
#passkey is a file that contains my API key and list ID and acts as a method of sharing 
#this file without sharing my api key, it is used only to delcare the key and list and
#Key can be generated via: https://nuthatch.lastelm.software/

from datetime import datetime
from datetime import date
from PIL import Image

ApiKey = passkey.Key
ListID = passkey.ListID

url = 'https://nuthatch.lastelm.software'

#execute "create_list" to generate a ListID. 
#This is the list that will be populated with 'new' birds
class Bird: #introudced class as many of the same parameters were being parsed around
    def __init__(self,Data): #fed data dict and extracts all used information
        self.ID = Data['id']
        self.Name = Data['name']
        self.SciName = Data['sciName']
        self.Family = Data['family']
        self.Order = Data['order']
        self.Regions = Data['region']
        #Above information is always present as it can be used as a search term (so can fill it in)
        #Below information seems to not always be present so have to use other methods
        try:
            self.Length = (float(Data['lengthMin']) + float(Data['lengthMax']))/2
        except:
            self.Length = 0
        try:
            self.Wingspan = (float(Data['wingspanMin']) + float(Data['wingspanMax']))/2
        except:
            self.Wingspan = 0
        
        self.Data = Data #above data tends to be parsed around a lot more. Still may want to access the actual data itself though for more niche purposes
        self.ImgUrls = []
        try:
            for x in Data['images']:
                self.ImgUrls.append(x)
        except:
            pass
        self.Audio = []
        try:
            for x in Data['recordings']:
                self.Audio.append(x)
        except:
            pass
        
    def add_to_list(self):
        headers = {
         'accept': 'application/json',
         'API-Key': f'{ApiKey}',
         'Content-Type': 'application/json'
        }
        json_data = {
         'birdId': self.ID,
         'description': f'{self.Name},{self.Order},{self.Length},{self.Wingspan}',
         'date-time': 'today',
         'location': 'string',
        }
        Response = requests.post(f'{url}/checklists/{ListID}/entries/{self.ID}',headers=headers,json=json_data)
        if Response.status_code == 200:
            return(True)
        else:
            return(False)    

    def get_sounds(self):
        try:
            for x in self.Audio:
                Link = x['file']
                Remark = x['rmk']
                if Remark == "":
                    print(f'{Link}')
                else:
                    print(f'{Link} : {Remark}')
        except: #sometimes birds do not have all data (so no audio available)
            headers = {
            'accept': 'application/json',
            'API-Key': f'{ApiKey}'
            }
            Response = requests.get(f'{url}/birds/{self.ID}',headers=headers)
            SoundData = Response.json()
            try:
                Audio = SoundData['recordings']
                self.Audio = Audio #redefines audio if none is found
                if len(Audio) == 0:
                    print("No audio found")
                    pass
                else:
                    for x in Audio:
                        Link = x['file']
                        Remark = x['rmk']
                        if Remark == "":
                            print(f'{Link}')
                        else:
                            print(f'{Link} : {Remark}')
            except:
                print("No audio found")
    
    def get_images(self):
        #print(self.ImgUrls)
        if len(self.ImgUrls) == 0:
            print("No images found")
        for x in self.ImgUrls:
            count =+ 1
            urllib.request.urlretrieve(x,f"BOTD{count}.jpg")
            img = Image.open(f"BOTD{count}.jpg")
            img.show()

    def info_string(self):
        RegList = ":"
        for x in range(len(self.Regions)):
            if x == len(self.Regions) - 1 and len(self.Regions)>1:
                print("and")
                RegList = f'{RegList} and {self.Regions[x]}'
            else:
                RegList = f'{RegList} {self.Regions[x]}'
        OutputStr = f"Todays bird is the {self.SciName} or the {self.Name}, it is a member of the {self.Order} order. It can be found in {RegList}. "
        if self.Wingspan == 0 and self.Length == 0:
            return(OutputStr)
        if self.Wingspan == 0 and self.Length != 0:
            return(OutputStr + f'The {self.Name} has an average length of {self.Length}')
        if self.Wingspan != 0 and self.Length == 0:
            return(OutputStr + f'The {self.Name} has an average wingpsan of {self.Wingspan}')
        if self.Wingspan != 0 and self.Length != 0:
            return(OutputStr + f'The {self.Name} has an average wingpsan of {self.Wingspan} and length of {self.Length} for a Wingspan:Length ratio of {round(self.Wingspan/self.Length,2)}')

def create_list(ListName): #need to refine this more but do not want to hit list limit
    headers = {
     'accept': 'application/json',
     'API-Key': f'{ApiKey}',
     'Content-Type': 'application/json'
    }
    json_data = {
        'name': f'{ListName}',
        'id': 'string',
    }
    Response = requests.post('https://nuthatch.lastelm.software/checklists', headers=headers, json=json_data)
    Data = Response.json()
    print(Data)
    return(Data)

def get_list(): #returns list of birds by ID and Date (for BotD)
    headers = {
    'accept': 'application/json',
    'API-Key': f'{ApiKey}'
    }
    params = {
     'pageSize': '100',
     'page': '1'
    }
    Response = requests.get(f'{url}/checklists/{ListID}/entries',headers=headers,params=params)
    Data = Response.json()
    Pages = math.ceil((Data['total']/100))
    #print(Pages)
    IDList = []
    DateList = []
    for x in Data['entities']:
        IDList.append(x['birdId'])
        DateList.append(x['date-time'])

    if Pages > 1:
        for x in range(2,Pages):
            params['page'] = x
            Response = requests.get(f'{url}/checklists/{ListID}/entries',headers=headers,params=params) 
            Data = Response.json
            for y in Data['entities']:
                IDList.append(y['birdId'])
                DateList.append(y['date-time'])
    return(IDList,DateList)

def get_bird(CommonName = "",Family = "",Order = "",New = True):
    
    headers = {
    'accept': 'application/json',
    'API-Key': f'{ApiKey}'
    }

    params = {
        'hasImg': 'true',
        'pageSize' : '100'
    }

    if CommonName != "":
        params['name'] = CommonName
    
    if Family != "":
        params['family'] = Family

    if Order != "":
        params['order'] = Order
    
    Response = requests.get(f'{url}/v2/birds', headers=headers, params=params)
    Data = Response.json()
    Total = Data['total']

    if Total == 0:
        print("No birds found :(")
        return
    
    PageSize = Data['pageSize']
    Pages = math.ceil(Total/PageSize) + 1 # for below loop to go need multiple pages (so increment it here)
    IDList,Dates = get_list()
    
    BirdList = []
    for Page in range(1,Pages+1): # makes a set of requests to stitch together all entries (to reduce requests)
        Response = requests.get(f'{url}/v2/birds?page={Page}',headers=headers,params=params)
        Data = Response.json()
        for x in Data['entities']:
            BirdList.append(x)
            

    TrimList = BirdList 
    # removes duplicates but preserves original in case nothing is left afterwards
    if New:
        for x in TrimList:
            FoundID = x['id']
            if str(FoundID) in IDList:
                TrimList.remove(x)
    
    if len(TrimList) == 0:
        print('No new birds found matching parameters :(')
        if len(BirdList) == 1:
            Target = 0
        else:
            Target = random.randrange(1,max(len(BirdList),1)) - 1
        RandBird = BirdList[Target]
        New = False    
    else:
        if len(TrimList) == 1:
            Target = 0
        else:
            Target = random.randrange(1,max(len(TrimList),1)) - 1
        RandBird = TrimList[Target]
    
    SelBird = Bird(RandBird)
    
    if New == True:
        SelBird.add_to_list()
    print(SelBird.info_string())
    SelBird.get_sounds()
    SelBird.get_images()

def get_bird_by_ID(ID):
    #not all entries seem to have recordings
    #this acts as an alternate way to grab recordings using a different request
    headers = {
     'accept': 'application/json',
     'API-Key': f'{ApiKey}'
    }
    Response = requests.get(f'{url}/birds/{str(ID)}',headers=headers)
    Data = Response.json()
    return(Data['name'],Data['family'])

def get_bird_of_the_day(CommonName = "",Family = "",Order = ""):
    Today = date.today()
    IDs,Dates = get_list()
    ISOList = []
    for x in Dates:
        item = datetime.fromisoformat(x)
        item = item.date()
        ISOList.append(item)
    #note that the below method can have issues with timezones
    if Today in ISOList:
        BirdID=IDs[ISOList.index(Today)] 
        Name,f = get_bird_by_ID(BirdID)
        get_bird(CommonName=Name,New=False)
    else:
        get_bird(CommonName=CommonName,Family=Family,Order=Order,New=True)

def get_stats(startdate="",enddate=""): #need to fix figure layout
    #This function scrapes the list for info based of order, wingspan and length

    headers = {
    'accept': 'application/json',
    'API-Key': f'{ApiKey}'
    }
    params = {
     'pageSize': '100',
     'page': '1'
    }
    Response = requests.get(f'{url}/checklists/{ListID}/entries',headers=headers,params=params)
    Data = Response.json()

    Pages = math.ceil((Data['total']/100))
    DescList = []
    DateList = []
    FamilyList = []
    LengthList = []
    WingspanList = []

    for x in Data['entities']:
        DescList.append(x['description'])
        DateList.append(x['date-time'])

    if Pages > 1:
        for x in range(2,Pages):
            params['page'] = x
            Response = requests.get(f'{url}/checklists/{ListID}/entries',headers=headers,params=params) 
            Data = Response.json
            for y in Data['entities']:
                DescList.append(y['description'])
                DateList.append(y['date-time'])
    
    for x in DescList:
        item = x.split(',')
        FamilyList.append(item[1])
        if item[2] == '0':
            #print("skipping zero (LENGTH)")
            pass
        else:
            LengthList.append(float(item[2]))
        if item[3] == '0':
            #print("skipping zero (WING)")
            pass
        else:
            WingspanList.append(float(item[3]))

    FamilyData = collections.Counter(FamilyList)
    Labels = []
    PieData = []
    
    for x in FamilyData:
        PieData.append(FamilyData[x])
        Labels.append(x)
    
    WingData = np.array(WingspanList)
    LengthData = np.array(LengthList)
    PieData = np.array(PieData)
    #print(WingData)
    #print(LengthData)
    plt.subplot(3,1,1)
    plt.hist(WingData,label="Wing Span Historgram",color='skyblue')
    plt.title("Wing Span Historgram")
    plt.ylabel('Occurences')
    plt.xlabel('Wingspan (cm)')
    plt.subplot(3,1,2)
    plt.hist(LengthData,label="Length Histogram",color = 'forestgreen')
    plt.ylabel('Occurences')
    plt.xlabel('Length (cm)')
    plt.title("Length Historgram")
    plt.subplot(3,1,3)
    plt.pie(PieData,labels=Labels)
    plt.title("Occurences of Orders Pie Chart")
    plt.tight_layout(pad=0.1)
    plt.show()
    #print(DescList)
    #print(DateList)

def add_unq_bird(Name,Order,Length=0,Wingspan=0): #if a bird not present in database can instead add it to the lsit (for purpose of stats)
    
    IDList,FamilyList = get_list()
    IntID = list(map(int,IDList))
    Lowest = min((min(IntID)),-1) 
    
    headers = {
     'accept': 'application/json',
     'API-Key': f'{ApiKey}',
     'Content-Type': 'application/json'
    }
    json_data = {
     'birdId': f'{Lowest}',
     'description': f'{Name},{Order},{Length},{Wingspan}',
     'date-time': 'today',
     'location': 'string',
    }    

    #By defining an ID as negative can avoid conflicting w/any future entries in list 
    Response = requests.post(f'{url}/checklists/{ListID}/entries/{Lowest}',headers=headers,json=json_data)
    if Response.status_code == 200:
        return(True)
    else:
        return(False)

