from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
import urllib
import operator

APIKEY = raw_input('enter API key: ')
USERNAME = raw_input('enter username: ')
ORGANIZATION = raw_input('enter team name: ')
SAVE_FOLDER = raw_input('enter the folder directory to save datasets: ')

BASE_URL = "https://{organization}.carto.com/user/{user}/". \
    format(organization=ORGANIZATION,
           user=USERNAME)
USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
auth_client = APIKeyAuthClient(api_key=APIKEY, base_url=USR_BASE_URL, organization=ORGANIZATION)

dataset_manager = DatasetManager(auth_client)
datasets = dataset_manager.all()

datasets_dict = {}
min_size = 0.000001 # for query by dataset size b/c already started sorted

for i in datasets:
    if round(i.table.size/1048576.00, 2) > min_size:
        case = {'size': round(i.table.size/1048576.00, 2)}
        datasets_dict[i.table.name] = case
    else:
        pass

sorted_datasets = sorted(datasets_dict.items(), key=operator.itemgetter(1))

non_exported = []

for keys, values in sorted_datasets:
    print(keys, values['size'])
    tablename = keys
    url = 'https://%s.carto.com/api/v2/sql?&api_key=%s&filename=%s.csv&format=csv&q=SELECT * FROM %s' % (USERNAME, APIKEY, tablename, tablename) 
    # print tablename
    try:
        dl_file = urllib.URLopener()
        dl_file.retrieve(url, SAVE_FOLDER+'/'+tablename+'.csv')
    except:
        non_exported.append(keys)
        
print 'List of non-exported datasets:', non_exported