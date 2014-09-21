from base_extractor import BaseExtractor
from mongo import misc
from mechanize import Browser
import hashlib, uuid, os, json, requests

class AddressAPIAccount():
  def __init__(self):
    account = misc.find_one({'type': 'address_api_account'})
    if not account:
      account = self.get_new_account()
      account.update({'type': 'address_api_account'})
      misc.insert(account)
    elif account.get('remaining') < 150:
      account = self.get_new_account()
      account.update({'type': 'address_api_account'})
      misc.update({'_id': account['_id']}, account)
    self.account = account

  def get_fake_email(self):
    return hashlib.md5(str(uuid.uuid4())).hexdigest() + "@monumentmail.com"

  def get_new_account(self):
    email = self.get_fake_email()
    password = str(uuid.uuid4())
    br = Browser()
    br.open(os.getenv('ADDRESS_API_ROOT_PAGE') + '/account/create')
    br.select_form(nr=0)
    br['email'] = email
    br['password'] = password
    br['firstname'] = 'Jon Doe'
    br['company'] = hashlib.md5(str(uuid.uuid4())).hexdigest()
    br.submit()
    br.open(os.getenv('ADDRESS_API_ROOT_PAGE') + '/account/keys')
    br.select_form(nr=3)
    br['name'] = str(uuid.uuid4())
    response = br.submit()
    account = json.loads(response.read())
    account.update({'email': email, 'password': password, 'remaining': 10000})
    return account

  def parse_address(self, s):
    misc.update({'type': 'address_api_account'}, {'$inc': {'remaining': -1}})
    query_string = {"auth-id": self.account['key_id'], "auth-token": self.account['token']}
    try:
      result = requests.post(os.getenv('ADDRESS_EXTRACTION_API'), params=query_string, data=s.encode("utf8")).json()
      line = result['addresses'][0]['line']
      surrounding = ' '.join(s.split("\n")[max(line-2, 0):line+2])
      if any([x in surrounding.lower() for x in ['unsubscribe', 'receive these emails']]):
        return None
      api_output = result['addresses'][0]['api_output'][0]
      return api_output.get('delivery_line_1','') + " " + api_output.get('last_line','')
    except (IndexError, KeyError, ValueError):
      return None

class AddresssExtractor(BaseExtractor):
    @staticmethod
    def extract(message, context):
      body = message.get('payload').get('body')
      parser = AddressAPIAccount()
      address = parser.parse_address(body)
      if address:
        return {'location': address}, {}
      else:
        return {}, {}
