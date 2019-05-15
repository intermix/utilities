import requests
import logging
import sys
import settings

class intermix(object):

    def __init__(self, api_token=""):

        self.logger = logging.getLogger(__name__)

        self.__BASE_URL__ = settings.API_URL
        self.__CLUSTER_TYPE__ = settings.CLUSTER_TYPE
        self.__API_TOKEN__ = api_token

    def api_request(self, cluster_id="", template="", params={}):

        base_params = {}
        base_params["cluster_type"] = self.__CLUSTER_TYPE__
        base_params["cluster_id"] = cluster_id

        endpoint_url = template % base_params

        #build params
        param_url = ""
        for key,val in params.iteritems():
         param_url = "{0}={1}&{2}".format(key,val,param_url)
        param_url = param_url[:-1]  #remove trailing &

        try:

            url = "%s/%s?%s" % (self.__BASE_URL__, endpoint_url, param_url)
            try:
                r = requests.post(url, headers={'Authorization': 'Token %s' % (self.__API_TOKEN__)})
            except:
                r = requests.post(url, headers={'Authorization': 'Token %s' % (self.__API_TOKEN__)}, verify=False)

            if r.status_code != 200:
                logging.critical("API request to %s failed %s", url, str(r))
                sys.exit()

        except Exception as e:
         logging.critical("Exception in API request %s", e)
         sys.exit()

        data = r.json()

        return data


    def get_users(self, cluster_id=""):

        params = {}
        template = "%(cluster_type)s/%(cluster_id)s/users"
        data = self.api_request(cluster_id=cluster_id, template=template, params=params)

        return data["data"]


    def get_groups(self, cluster_id=""):

        params = {}
        template = "%(cluster_type)s/%(cluster_id)s/groups"
        data = self.api_request(cluster_id=cluster_id, template=template, params=params)

        return data["data"]
