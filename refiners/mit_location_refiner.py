import requests

from base_refiner import BaseRefiner

class MITLocationRefiner(BaseRefiner):
    @staticmethod
    def refine(results, context):
       result = {}
       location = results.get('location')
       if location is not None:
           data = requests.get('http://whereis.mit.edu/search?type=query&q=' + location).json()
           if len(data) > 0: # Note: never seems to return more than one result, should be ok to blindly use 0th element if it exists.
               result['mit_location'] = True
               result['latitude'] = data[0]['lat_wgs84']
               result['longitude'] = data[0]['long_wgs84']
               if location.find('MIT') == -1 and location.find('Massachusetts Institute of Technology') == -1:
                   result['location'] = 'MIT ' + location
       return result, {}
