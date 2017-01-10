import requests


class Pinstabot(object):

    def __init__(self, user_name, pwd):
        self.user_name = user_name
        self.pwd = pwd
        self.sv = requests.session()
        self.csrf_token = ""

    '''
    Now preparing for logging in. First updating the cookies,
    setting up login payload (for data = ?) then updating request headers
    then finally posting a request for logging in with preset data.

    While logging in the request expects the 'csfrtoken' generated as the
    response of the get request request of visiting the login page.
    '''
    def login(self):
        # Setting up cookies (for request cookies) for posting
        self.sv.cookies.update({'sessionid': '',
                                'mid': '',
                                'ig_pr': '1',
                                'ig_vw': '1295',
                                'csrftoken': '',
                                's_network': '',
                                'ds_user_id': requests.get("https://www.instagram.com/{}/?__a=1".format(self.user_name)).json()['user']['id'],
                                })

        self.login_payload = {'username': '{}'.format(self.user_name),
                           'password': '{}'.format(self.pwd)
                           }

        # Setting up headers (for request headers) for posting
        self.sv.headers.update({'Accept-Encoding': 'gzip, deflate, br',
                                'Accept-Language': "en-US,en;q=0.5",
                                'Connection': 'keep-alive',
                                'Content-Length': '0',
                                'Host': 'www.instagram.com',
                                'Origin': 'https://www.instagram.com',
                                'Referer': 'https://www.instagram.com/',
                                'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0",
                                'X-Instagram-AJAX': '1',
                                'X-Requested-With': 'XMLHttpRequest'
                                })

        #feeding the request header with the csfrtoken captured as the
        # response of visiting the login page get() request response
        self.sv.headers.update({'X-CSRFToken': self.sv.get("https://www.instagram.com").cookies['csrftoken']})
        login = self.sv.post(url="https://www.instagram.com/accounts/login/ajax/", data=self.login_payload, allow_redirects=True)
        self.sv.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.csrf_token = login.cookies['csrftoken']
        if login.status_code == 200:
            print('Login Successful!')
            #login successful

    def logout(self):
        logout_payload = {'csrfmiddlewaretoken': self.csrf_token}
        logout = self.sv.post('https://www.instagram.com/accounts/logout/', data=logout_payload)
        if logout.status_code == 200:
            print('Logout Successful!')

    def giveUserPics(self, targetUserName, noOfPics):
        finalList = []
        tempList = []
        firstNode = self.sv.get('http://www.instagram.com/{}/?__a=1'.format(targetUserName)).json()['user']['media']['nodes'][0]
        tempList.append(firstNode['display_src'])

        query_payload = {
            "q": "ig_user(" + firstNode['owner']['id'] + ") { media.after(" + firstNode['id'] + ", +" + str(noOfPics-1) + ") {  count,  nodes {    caption,    code,    comments {      count    },    comments_disabled,    date,    dimensions {      height,      width    },    display_src,    id,    is_video,    likes {      count    },    owner {      id    },    thumbnail_src,    video_views  },  page_info} }",
            "ref": "",
            "query_id": "17846611669135658"}

        query = self.sv.post(url="https://www.instagram.com/query/", data=query_payload, allow_redirects=True)
        for x in query.json()['media']['nodes']:
            tempList.append(x['display_src'])

        toremove = ['/p960x960/', '/s960x960/', '/p750x750/', '/s750x750/', '/p640x640/', '/s640x640/', '/p480x480/', '/s480x480/']
        for raw_url in tempList:
            #removing anything after .jpg
            raw_url = raw_url.replace(raw_url[raw_url.find('?ig_'):], "")

            #removing images s640x640 thigns...
            if any(x in raw_url for x in toremove) is True:
                match = next(x for x in toremove if x in raw_url)
                raw_url = raw_url.replace(match, '/')

            finalList.append(raw_url)
        del tempList
        return(finalList)
