class Message(object):
  def __init__(self, data):
    self.d = data

  def get(self, k, v=None):
    return self.d.get(k, v)

  def __getitem__(self, key):
    return self.get(key)

  def get_header(self, name):
    for header in self.d['payload']['headers']:
      if header['name'] == name:
        return header['value']
    return None
