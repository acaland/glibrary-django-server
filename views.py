from django.http import HttpResponse,HttpResponseRedirect, HttpResponseNotFound
from django.utils.encoding import smart_str, smart_unicode
from django.views.decorators.csrf import csrf_exempt
import datetime, os 
import httplib, urlparse, urllib
import mdclient, mdinterface, json
import MySQLdb
import datetools
#import sys, os, time, cgi, urllib, urlparse
#from M2Crypto import m2urllib2 
#from M2Crypto import m2, SSL, Engine


gridops = {
        'deroberto' : {
                'file_download' : 66,
                'metadata_reading' : 67,
                'collection_schema_retrieval' : 68 
        },
        'medrepo' : {
               'file_download' : 71,
                'metadata_reading' : 70,
                'collection_schema_retrieval' : 69
        },
        'chinarelics' : {
               'file_download' : 72,
                'metadata_reading' : 73,
                'collection_schema_retrieval' : 74
        }
}       
        
        



def usertrackingdb_execute(query, args=None):
        
        db_host = 'liferay.ct.infn.it'
        db_user = 'tracking_user' 
        db_passwd = 'usertracking'
        db_name='userstracking'
        
        db=MySQLdb.connect(db_host, db_user, db_passwd, db_name)
        
        c=db.cursor()
        ret = c.execute(query, args)
        rowid = c.lastrowid
        #print ret
        #results = c.fetchall()
        return ret, rowid


def usertrackingdb_insert_grid_interaction(liferay_user, remote_address, grid_op, grid_id, robot_dn, robot_serial, vo, vo_role):

        query = """INSERT INTO GridInteractions (common_name, tcp_address, timestamp, grid_interaction, 
                        grid_id, robot_certificate, proxy_id, virtual_organization, fqan, user_description, status) 
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        #remote_address = request.environ['REMOTE_ADDR']+':'+str(request.environ['REMOTE_PORT'])
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args = (liferay_user, remote_address, current_date, grid_op,
                        grid_id, robot_dn, robot_serial, vo, vo_role, '', 'COMPLETED')
	print args
        try:
                usertrackingdb_execute(query, args)
        except Exception, e:
                print "Something went wrong accessing the user tracking DB"
        	print e

def usertrackingdb_start_grid_interaction(liferay_user, grid_op, grid_id, vo_role):
        
        query = """INSERT INTO ActiveGridInteractions (common_name, tcp_address, timestamp, grid_interaction, 
                        grid_id, robot_certificate, proxy_id, virtual_organization, fqan, user_description, status) 
                        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        remote_address = request.environ['REMOTE_ADDR']+':'+str(request.environ['REMOTE_PORT'])
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args = (liferay_user, remote_address, current_date, grid_op,
                        grid_id, robot_dn, robot_serial, vo, vo_role, '', 'STARTED')
        try:
                ret, rowid = usertrackingdb_execute(query, args)
                #print "logged Encryption start successfully"
                return rowid
        except:
                print "Something went wrong accessing the user tracking DB"     
                                

def usertrackingdb_complete_grid_interaction(id, description='', status='COMPLETED'):
        
        query = """INSERT INTO GridInteractions (common_name, tcp_address, timestamp, grid_interaction, 
                        grid_id, robot_certificate, proxy_id, virtual_organization, fqan) 
                        SELECT common_name, tcp_address, timestamp, grid_interaction, 
                        grid_id, robot_certificate, proxy_id, virtual_organization, fqan FROM ActiveGridInteractions WHERE id=%s""" % id        
        try:
                ret, rowid = usertrackingdb_execute(query)
        except:
                print "Something went wrong accessing the user tracking DB - copia da active a grid"    
                return  
        query = "UPDATE GridInteractions SET user_description=%s, status=%s WHERE id=%s"
        args = (description, status, rowid)
        
        try:
                usertrackingdb_execute(query, args)
        except:
                print args
                print "Something went wrong accessing the user tracking DB - update"
                return
                
        query = "DELETE FROM ActiveGridInteractions WHERE id=%s" % id
        
        try:
                #print "id to delete ", id
                usertrackingdb_execute(query)
        except:
                print query
                print "Something went wrong accessing the user tracking DB - delete"
                return
        


def get_proxy(certificate_serial, vo, attribute, proxy_file):

    #print request.environ
    print "call to get_proxy"
    etokenserver = "myproxy.ct.infn.it"

    server_url = "http://myproxy.ct.infn.it:8082/eTokenServer/eToken/%s?voms=%s:%s&proxy-renewal=false&disable-voms-proxy=true" % (certificate_serial, vo, attribute)
    print server_url
    f = urllib.urlopen(server_url)
    proxy = open(proxy_file, "w");
    proxy.write(f.read())
    f.close()
    proxy.close()
    os.chmod(proxy_file, 0600)


def get_proxy2(vo):

	if vo == "vo.indicate-project.eu":
		proxy_file = '/tmp/indicate_proxy'
		robot_serial = '26467'
		certificate_md5 = '678db46f8ccd12ccb240cd2f91d18205'
		attribute = '/vo.indicate-project.eu'
	elif vo == "vo.aginfra.eu":
		robot_serial = '25667'
		attribute = '/vo.aginfra.eu'
		certificate_md5 = '62b53afcb320386d6ad938d3d2fdfbfc'
		proxy_file = '/tmp/aginfra_proxy'
	elif vo == "vo.earthserver.eu":
		robot_serial = "25668"
		proxy_file = '/tmp/earthserver_proxy'
		certificate_md5 = '36beeec99546392a0fd6692242fef938'
		attribute = '/vo.earthserver.eu'
	elif vo == "vo.dch-rp.eu":
		robot_serial = '26581'
		proxy_file = '/tmp/dchrp_proxy'
		certificate_md5 = '876149964d57df2310eb3d398f905749'
		attribute='/vo.dch-rp.eu'
	elif vo == "eumed":
		proxy_file = '/tmp/eumed_proxy'
		certificate_md5 = 'bc681e2bd4c3ace2a4c54907ea0c379b'
		attribute = '/eumed'
	else:
		robot_serial = '25207'
		proxy_file = '/tmp/cataniasg_proxy'
		certificate_md5 = '332576f78a4fe70a52048043e90cd11f'
		attribute = '/' + vo

    	#print request.environ
	print "call to get_proxy 2"
    	#etokenserver = "myproxy.ct.infn.it"

    	#server_url = "http://myproxy.ct.infn.it:8082/eTokenServer/eToken/%s?voms=%s:%s&proxy-renewal=false&disable-voms-proxy=true" % (certificate_serial, vo, attribute)
	server_url = "http://etokenserver.ct.infn.it:8082/eTokenServer/eToken/%s?voms=%s:/%s&proxy-renewal=false&disable-voms-proxy=true" % (certificate_md5, vo, attribute)
	print server_url
	f = urllib.urlopen(server_url)
	proxy = open(proxy_file, "w");
	proxy.write(f.read())
	f.close()
	proxy.close()
	os.chmod(proxy_file, 0600)
	return proxy_file




def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>Sono le  %s.</body></html>" % now
    return HttpResponse(html)

	
# Retrieves the data of the 'directory' parameter, returning also the thumbnail of each entry.
# Accepts start and limit parameters, and also filtering (numeric/list filters). 
#   .../getData/directory/    ex.: http://glibrary.ct.infn.it/django/getData/deroberto2/Entries/
#	Examples with not compulsory parameters:
#			http://glibrary.ct.infn.it/django/glib/deroberto2/Entries/Scans/?start=51
#			http://glibrary.ct.infn.it/django/glib/deroberto2/Entries/Scans/?start=3&filter[0][data][comparison]=gt
#				&filter[0][data][type]=numeric&filter[0][data][value]=2&filter[0][field]=PagNum
#				&filter[1][data][comparison]=lt&filter[1][data][type]=numeric&filter[1][data][value]=4
#				&filter[1][field]=PagNum
def getData(request,directory):
	repoArr=directory.split('/')
	repo=str(repoArr[0])
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	atr,types=client.listAttr(directory)
	
	# Taking the possible parameters
	if request.GET.has_key('start'):
		start=int(request.GET.getlist('start')[0])
	else:
		start=0
	#if request.GET.has_key('limit'):
	#	limit=start+int(request.GET.getlist('limit')[0])
	#else:
	limit=50
	
	filterList=[]
	i=0
	# Retrieving the possible filters
	while request.GET.has_key('filter['+str(i)+'][field]'):
		filter={'data':{'type': '','value':'','comparison':'eq'},'field':''}
		filter['field']=request.GET.getlist('filter['+str(i)+'][field]')[0]
		filter['data']['type']=request.GET.getlist('filter['+str(i)+'][data][type]')[0]
		if filter['data']['type']=='numeric':
			filter['data']['comparison']=request.GET.getlist('filter['+str(i)+'][data][comparison]')[0]
		filter['data']['value']=request.GET.getlist('filter['+str(i)+'][data][value]')
		filterList.append(filter)
		i=i+1
		#print 'filter->',filter['field'],'=',filter['data']['value']
	cad=''
	# Creating the query from the filters' information
	for i in range(len(filterList)):
		longit=len(filterList[i]['data']['value'])
		for j in range(longit):
			if filterList[i]['data']['comparison']=='eq':
				comparator='='
			elif filterList[i]['data']['comparison']=='lt':
				comparator='<'
			elif filterList[i]['data']['comparison']=='gt':
				comparator='>'	
			if j == (longit-1):
				cad=cad+filterList[i]['field']+comparator+'"'+filterList[i]['data']['value'][j]+'" '
				#print 'filterList',filterList[i]['field'],'="',filterList[i]['data']['value'][j],'"'
			else:
				cad=cad+filterList[i]['field']+comparator+'"'+filterList[i]['data']['value'][j]+'" or '
				#print 'filterList',filterList[i]['field'],'="',filterList[i]['data']['value'][j],'" or'
		cad=cad+ 'and '
	
	j=0
	resultado=[]
	#client.getattr(directory,atr)
	atr0=atr[0]
	atr[0]='/'+directory+':'+atr[0]
	atr.append('/'+directory+':FILE')
	atr.append('/'+repo+'/Thumbs:Data')
	# Making the query to the gLibrary server
	if(directory=='miguel'):
		client.selectAttr(atr,'limit '+str(limit)+' offset '+str(start))
	else:
		client.selectAttr(atr,str(cad)+'Thumb='+repo+'/Thumbs:FILE limit '+str(limit)+' offset '+str(start))
	# Obtaining the data received and preparing it to be returned to the server
	while not client.eot():
		val=client.getSelectAttrEntry() #file,val=client.getEntry()
		resultado.insert(j,{})
		for i in range(len(val)):
			resultado[j][atr[i]]=val[i]
		resultado[j][atr0]=val[0]
		j=j+1
	# Asking for the number of entries returned
	if len(cad)>5:
		client.selectAttr(['count('+directory+':FILE)'],str(cad[0:-5]))
	else:
		client.selectAttr(['count('+directory+':FILE)'],'')
	total=client.getSelectAttrEntry()
	
	# Making the jsonData structure to be returned
	jsonData= json.dumps({'total':total,'records':resultado})
	if request.GET.has_key('callback'):
		html = request.GET.getlist('callback')[0]+"(%s);" % jsonData
		return HttpResponse(html, content_type="text/javascript")
	else:
		html = "%s" % jsonData
		return HttpResponse(html)

# Returns the tree structure of the selected treenode on ExtJS, codified in Json format
# Just for learning purposes
def get_tree(request):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	resultado=[]
	if request.method != 'OPTIONS':
		# retrieves the data of the corresponding node (parameter 'node')
		client.listEntries(request.GET.getlist('node')[0])
		while not client.eot():
			file,val=client.getEntry()
			# process the data creating the tree structure
			if val[0].startswith('collection'):
				resultado.append({'id':file,'text':file,'leaf':False})
			else:
				resultado.append({'id':file,'text':file,'leaf':True})
	# creates the jsonData structure that will be returned
	jsonData = json.dumps(resultado)
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response

# Returns the tree structure of the 'tree_id' directory parameter, codified in Json format
# Just for learning purposes
def get_tree_dir(request,tree_id):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	resultado=[]
	# retrieves the data of the corresponding node (parameter 'node')
	client.listEntries(tree_id)
	while not client.eot():
		file,val=client.getEntry()
		# process the data creating the tree structure
		if val[0].startswith('collection'):
			resultado.append({'id':file,'text':file,'leaf':False})
		else:
			resultado.append({'id':file,'text':file,'leaf':True})
	# creates the jsonData structure that will be returned
	jsonData = json.dumps(resultado)
	html = "%s" % jsonData
	response=HttpResponse(html)
	return response

# Returns the tree structure of the 'node' parameter selected in ExtJS according to the repository
# information (/repository/Types). Requires the name of the repository and also the 'id' of the node
# from where we want to get the tree: .../getTree/repositoryName/?node=0
# Examples:  http://glibrary.ct.infn.it/django/getTree/deroberto2/?node=1
def getTree(request,repo):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	resultado=[]
	# access to the directory
	client.cd(repo+'/Types')
	if request.method != 'OPTIONS':
		# retrieve information of the selected node
		client.selectAttr(['.:TypeName','FILE','Path','VisibleAttrs'],'ParentID='+request.GET.getlist('node')[0])
		# process information to create the tree structure
		while not client.eot():
			entry=client.getSelectAttrEntry()
			resultado.append({'text':entry[0],'id':entry[1],'path':entry[2],'leaf':False, 'visibleAttrs':entry[3]})
		# check if the selected node is a leaf to mark it as that
		for i in range(len(resultado)):
			client.selectAttr(['.:TypeName','FILE'],'ParentID='+resultado[i]['id'])
			if(client.eot()):
				resultado[i]['leaf']=True
				resultado[i]['iconCls']= 'folder-icon'
			else:
				while not client.eot():
					client.getSelectAttrEntry()
	# creates the jsonData structure and the response that will be returned
	jsonData=json.dumps(resultado)
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response

# Returns a list with the possible selectable values on each of the filters (list ones),
# attending to the filter options previously selected. Requires the name of the directory and the
# 'filterData' parameter with the information of the filters actually applied:
# 		.../getFilterValues/repositoryName/?filterData=[]
# Examples:  http://glibrary.ct.infn.it/django/getFilterValues/medrepo/
#				?filterData=[{"field":"Tipology","data":{"type":"list","value":["religiosa"]}}]
def getFilterValues(request,directory):
	repoArr=directory.split('/')
	repo=str(repoArr[0])
	#takes the filterData parameter with the data of the currently applied filters
	if request.GET.has_key('filterData'):
		filterData=json.loads(request.GET.getlist('filterData')[0])
		
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	#directory='/'+repo+'/Entries'
	result=[]
	if request.method != 'OPTIONS':
		# retrieves the filterable attributes
		client.selectAttr(['/'+repo+'/Types:FilterAttrs'],'Path="/'+directory+'"')
		entry=client.getSelectAttrEntry()
		filterAttrs=entry[0].split(' ')
		
		# for each of the filterable attributes (list ones) we have to update their possible values...
		for k in range(len(filterAttrs)):
			pet=''
			#...so for each active filter, we check that same attribute is not one of the active...
			for i in range(len(filterData)):
				#...filters. (We don't need to update the values of the active filters)
				if filterAttrs[k]!=filterData[i]['field']:
					if filterData[i]['data']['type']!='numeric':
						# We start creating the query. Adding the current active filters...
						for j in range(len(filterData[i]['data']['value'])):
							#...with all the different values selected in that active filter
							if j < len(filterData[i]['data']['value'])-1:
								pet=pet+str(filterData[i]['field'])+'="'+str(filterData[i]['data']['value'][j])+'" or '
							else:
								pet=pet+str(filterData[i]['field'])+'="'+str(filterData[i]['data']['value'][j])+'" '
						# If it is not the last filter active, we keep on creating the whole query.
						if i < len(filterData)-1 and (filterData[i+1]['field']!=filterAttrs[k] or i+1 < len(filterData)-1) and filterData[i+1]['data']['type']!='numeric':
							pet=pet+' and '
			# finally we add the distinct clause to the query and execute it...
			if pet.endswith('and '):
				pet=pet[0:-4]
			client.selectAttr([directory+':'+filterAttrs[k]],pet+'distinct')
			options=[]
			#...retrieving all the new possible filter options for that attribute...
			while not client.eot():
				entry=client.getSelectAttrEntry()
				if entry[0]!='':
					options.append(entry)
			#...and adding those options to the result structure, repeating the process for the...
			#...rest of the filterable attributes
			result.append(options)
	# creates the jsonData structure and the response that will be returned
	jsonData=json.dumps(result)
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response

# Returns a personalised json data structure (learning purposes)
def data(request):
	jsonData='{"total": 2, "data": [{"FileName": "Prueba", "TypeID": "tipo1", "CategoryIDs": "cat1"},{"FileName": "OtroTest", "TypeID": "tipo2", "CategoryIDs": "cat2"}]}'
	if request.GET.has_key('callback'):
		html = request.GET.getlist('callback')[0]+"(%s);" % jsonData
	else:
		html = "%s" % jsonData
	return HttpResponse(html)

# Builds up and returns a Json data structure with information to define and construct on ExtJS
# the grid panel, the fields that define the store that will keep/store the data recieved from 
# the server, and the columns of the grid, ready to show the visible attributes with the specified
# column width, and also the applyable filters and their type. Taking into account the repository information
# (/repositoryName/Types:VisibleAttrs, ColumnWith, FilterAttrs)
# 			.../getStructuresInfo/directory/
#		Example:   http://glibrary.ct.infn.it/django/getStructuresInfo/deroberto2/Entries/Scans/
def metadata(request,directory):
	repoArr=directory.split('/')
	repo=repoArr[0]
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	#dirVisAttrs='/'+repo+'/Entries'
	# retrieving information of the attributes and the columns
	client.selectAttr(['/'+repo+'/Types:VisibleAttrs','ColumnWidth','FilterAttrs','ColumnLabels'],'Path="/'+directory+'"')
	entry=client.getSelectAttrEntry()
	visAttrs=entry[0].split(' ')
	lenAttrs=entry[1].split(' ')
	filterAttrs=entry[2].split(' ')
	labelAttrs=entry[3].split(',')
	atr,types=client.listAttr(directory)
	#atr.append('/'+directory+':FILE')
	#types.append('int')
	fields=[]
	columns=[]
	filters=[]
	if request.method != 'OPTIONS':
		# starting building the data structured to be returned, the 'fields' array that will
		# have the info for the store of the database attributes to be mapped and the 'columns' one
		# that with the information to display the columns of the grid on ExtJS
		for i in range(len(atr)):
			# setting the type of data of the fields
			if types[i]=='int':
				fields.append({'name': atr[i], 'mapping': atr[i],'type':'int'})
			else:
				fields.append({'name': atr[i], 'mapping': atr[i]})
			# default column definition
			columns.append({'align': 'left', 'css': 'vertical-align: middle;', 'header': '<font face="verdana">'+atr[i]+'</font>', 'width': 80, 'dataIndex': atr[i], 'colType': types[i], 'hidden':True, 'sortable': True })
			if(atr[i].endswith('Description')):
				columns[i]['id']='descrip'
			# setting visible attributes
			for j in range(len(visAttrs)):
				if visAttrs[j]==atr[i]:
					columns[i]['width']=int(lenAttrs[j])
					columns[i]['hidden']=False
		# extra fields to be able to display the thumbnails
		fields.append({'name': '/'+repo+'/Thumbs:Data', 'mapping': '/'+repo+'/Thumbs:Data'})
		fields.append({'name': '/'+directory+':FILE', 'mapping': '/'+directory+':FILE'})
		# reordering the attributes so that they will be displayed in the proper order (VisibleAttrs)
		for i in range(len(visAttrs)):
			for j in range(len(columns)):
				if(visAttrs[i]==columns[j]['dataIndex']):
					# correction to display the thumbnails
					if(columns[j]['dataIndex']=='Thumb'):
						columns[j]['id']='thumb'
						columns[j]['dataIndex']='/'+repo+'/Thumbs:Data'
					col=columns[j]
					columns.remove(col)
					columns.insert(i,col)
		# constructing data for the filters configuration
		for i in range(len(filterAttrs)):
			options=[]
			if filterAttrs[i]!='PagNum' and filterAttrs[i]!='Size':
				# retrieving the possible values for the actual filter (filterAttrs[i]
				client.selectAttr([directory+':'+filterAttrs[i]],'distinct')
				while not client.eot():
					entry=client.getSelectAttrEntry()
					if entry[0]!='':
						options.append([entry[0]])
				# adding the configuration of the current filter to the filters array
				filters.append({'type': 'list', 'dataIndex': filterAttrs[i], 'labelField': 'filter'+filterAttrs[i], 'filterList':options})
			else:
				filters.append({'type': 'numeric', 'dataIndex': filterAttrs[i]})
	# creates the jsonData structure and the response that will be returned
	jsonData= json.dumps({'metadata':{'root': 'records','totalProperty': 'total','fields': fields,'custom':'pruebaaaa'},'columns': columns,'filters': filters})
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response

# Returns an html structure with the hyperlinks of the available replicas of a file to be
# able to download them. The parameter 'id' is the number of the file we want the replicas from.
def getLinks(request,repo,id):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	client.cd('/'+repo+'/Replicas')
	resultado={'autoEl': { 'html': ''}}
	if request.method != 'OPTIONS':
		# retrieves the availables surls of the file
		client.selectAttr(['.:surl'],'ID='+id)
		# constructs the structure with the links of the replicas
		while not client.eot():
			link=client.getSelectAttrEntry()[0]
			resultado['autoEl']['html']=resultado['autoEl']['html']+'<a href="http://glibrary.ct.infn.it/django/download/'+link.lstrip("https://")+'" TARGET="_blank">'+link+'</a><br>'
	# creates the jsonData structure and the response that will be returned
	jsonData= json.dumps(resultado)
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	print "response: %s", response
	return response

# Returns a Json data structure with the information of the available replicas of a file, contaning
# the download links, and some extra data like latitude and longitude of the store element they
# are stored in, the name of the SE, or if it is active or not. Requires two parameters, the repository name and 'id'
# The parameter 'id' is the number of the file we want the replicas from.
# 			.../django/getLinks/repositoryName/id/
#		Example:  http://glibrary.ct.infn.it/django/getLinks/deroberto2/765/
def getLinks2(request,repo,id):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	storages=[]
	# gets information of the enabled hosts (SE)...
	client.selectAttr(['/deroberto2/Storages:Host','Enabled'],'')
	# ...and creates a structure with that info
	while not client.eot():
		entry=client.getSelectAttrEntry()
		storages.append({'name':entry[0],'enabled':entry[1]})
	client.cd('/'+repo+'/Replicas')
	resultado=[]
	if request.method != 'OPTIONS':
		# retrieves the links of the replicas of the selected file
		client.selectAttr(['.:surl','enabled'],'ID='+id)
		while not client.eot():
			entry=client.getSelectAttrEntry()
			link=entry[0]
			enabled=entry[1]
			#downLink=link.lstrip("https://")
			if link.startswith('https://'):
				downLink=link[8:]
			else:
				downLink=link[7:]
			print "downlink: ", downLink
			#print "link is: ", downLink
			# checks if the SE of the current replica is enabled...
			#for i in range(len(storages)):
			#	if downLink.startswith(storages[i]['name']):
			#		enabled=storages[i]['enabled']
			#...and adds the data of that replica to the data structure to be returned
			if downLink.startswith("infn-se-03"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'37.524971','lng':'15.071976','name':'INFN-CATANIA','enabled':enabled})
			elif downLink.startswith("prod-se-03"):
				resultado.append({'link': '<a href=/glibrary/download/'+downLink+' TARGET="_blank">Download</a>','lat':'37.525077','lng':'15.073253','name':'INFN-SE','enabled':enabled})			
			elif downLink.startswith("gridsrv3-4.dir.garr.it"):
				resultado.append({'link': '<a href=/glibrary/download/'+downLink+' TARGET="_blank">Download</a>','lat':'41.899131','lng':'12.511935','name':'GARR-SE','enabled':enabled})
			elif downLink.startswith("se.reef.man.poznan.pl"):
				resultado.append({'link': '<a href=/glibrary/download/'+downLink+' TARGET="_blank">Download</a>','lat':'52.411922','lng':'16.916131','name':'POZNAN-SE','enabled':enabled})
			elif downLink.startswith("unict-dmi-se-01"):
				resultado.append({'link': '<a href="/glibrary/download/'+downLink+'"/ TARGET="_blank">Download</a>','lat':'37.525077','lng':'15.073253','name':'DMI UNICT','enabled':enabled})
			elif downLink.startswith("unime-se-01"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'38.259842','lng':'15.599223','name':'UNIME','enabled':"0"})
			elif downLink.startswith("unict-diit-se-01"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'37.525077','lng':'15.073253','name':'DIIT','enabled':"0"})
			elif downLink.startswith("inaf-se-01"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'37.528779','lng':'15.071746','name':'INAF','enabled':"0"})
			elif downLink.startswith("unipa-se-01"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'38.1166667','lng':'13.3666667','name':'UNIPA','enabled':"0"})
			elif downLink.startswith("eunode4"):
				resultado.append({'link': '<a href="http://glibrary.ct.infn.it/django/download/'+downLink+'" TARGET="_blank">Download</a>','lat':'39.970806','lng':'116.411133','name':'BEIJING','enabled':enabled})
			elif downLink.startswith("earth.eo.esa.int"):
				resultado.append({'link': '<a href="http://'+downLink+'" TARGET="_blank">Download</a>','lat':'41.900233','lng':'12.683287','name':'ESA','enabled':enabled})
	#print "resultado:", resultado
	# creates the jsonData structure and the response that will be returned
	jsonData= json.dumps(resultado)
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response

# Allows to be able to download the selected replica by passing it the link to download as a parameter
# it uses the robot certificate to allow the download.
def download(request,link):
	#link = "https://infn-se-01.ct.pi2s2.it/dpm/ct.pi2s2.it/home/cometa/deroberto/busta23/001_Il_Rifugio_fronte.pdf"
	#print "sono all'inizio"
	print "COOKIES: ", request.COOKIES
	if link.startswith("eunode4"):
		proxy = '/tmp/euchina_proxy'
		robot_dn = '/C=IT/O=INFN/OU=Robot/L=COMETA/CN=Robot: Digital Repository of China Relics - Roberto Barbera'
		robot_serial = '24301'
		get_proxy('24301', 'euchina', '/euchina', proxy)
	elif 'eumed' in link:
		print "VO: eumed"
		proxy = get_proxy2('eumed')
	else:
		print "VO: other" 
		#robot_dn = '/C=IT/O=INFN/OU=Robot/L=Catania/CN=Robot: INDICATE e-Cultural Science Gateway - Antonio Calanducci'
		#robot_serial = '26467'
		#proxy = '/tmp/indicate_proxy'
		#get_proxy('26467', 'vo.indicate-project.eu', '/vo.indicate-project.eu', proxy)
		proxy = get_proxy2('vo.dch-rp.eu')
		print "ma come entro qui?"
	#print "sono alla fine"
	link = "https://%s" % link
	#print "link: %s" % link
	#return HttpResponse("<html><body>" + link + "</body></html>")
	#proxy = '/tmp/indicate_proxy'
	#get_proxy('19250', 'vo.indicate-project.eu', '/vo.indicate-project.eu', proxy)
	se = urlparse.urlparse(link).netloc
	#print "link: ", link
	#print "host: ", host
	#print request.META['REMOTE_ADDR']
	#print request.META['HTTP_X_FORWARDED_FOR']
	#print request.META['HTTP_X_FORWARDED_HOST']

	print "REMOTE_ADDR: ", request.META['REMOTE_ADDR']
	if 'HTTP_X_FORWARDED_FOR' in request.META:
		print "HTTP_X_FORWARDED_FOR: ", request.META['HTTP_X_FORWARDED_FOR']
	#print request.META['HTTP_X_FORWARDED_HOST']

	if se in ['infn-se-03.ct.pi2s2.it', 'vega-se.ct.infn.it','se.reef.man.poznan.pl','prod-se-03.ct.infn.it','gridsrv3-4.dir.garr.it']:
		if 'HTTP_X_FORWARDED_FOR' in request.META:
			headers = {"X-Auth-Ip": request.META['HTTP_X_FORWARDED_FOR']}
		else:
			headers = {"X-Auth-Ip": request.META['REMOTE_ADDR']}
		path = "/%s" % urlparse.urlparse(link).path
	else:   #old DPM-HTTP implementation
		headers = {}
		if 'HTTP_X_FORWARDED_FOR' in request.META:
			path = "/%s?authip=%s" % (urlparse.urlparse(link).path, request.META['HTTP_X_FORWARDED_FOR'])
		else:
			path = "/%s?authip=%s" % (urlparse.urlparse(link).path, request.META['REMOTE_ADDR'])


	
	#path = "%s?authip=%s" % (urlparse.urlparse(link).path, request.META['REMOTE_ADDR'])
	print "path: ", path
	conn = httplib.HTTPSConnection(se, cert_file=proxy, key_file=proxy)
	try:
		conn.request("GET", path, None, headers)
	except Exception, e:
		print e
		return HttpResponseNotFound("Network error: %s" % e)
	resp = conn.getresponse()
	#print "resp: ", resp
	print resp.status
	print resp.reason
	print resp.getheaders()
	redirect_url = resp.getheader("location")
	if redirect_url == None:
		output = resp.read()
		conn.close()
		return HttpResponseNotFound("replica (%s) not found<br>%s" % (link, output))
	print redirect_url
	conn.close()
	#if "/home/cometa/deroberto" in link:
	#	repo = "deroberto"
	#	vo = "vo.indicate-project.eu"
	#elif "/home/cometa/glibrary/medrepo" in link:
	#	repo = "medrepo"
	#	vo = "vo.indicate-project.eu"
	#elif "/home/euchina/relicrep" in link:
	#	repo = "chinarelics"
	#	vo = "euchina"

    #    remote_address = request.META['REMOTE_ADDR']+':'+str(request.META['REMOTE_PORT'])
	# user tracking db not accessible anymore from glibrary
	#usertrackingdb_insert_grid_interaction("guest", remote_address, gridops[repo]['file_download'],  link, robot_dn, robot_serial, vo, vo)    
	#return(HttpResponse(redirect_url))
	#response = HttpResponse("ciao mondo", content_type='text/plain') 
	#response['Content-Disposition'] = 'inline; filename=pappo.txt'
	#return response
	return HttpResponseRedirect(redirect_url)
	#key = '/tmp/proxy2'
	#cert = '/tmp/proxy2'
	#url = link = "https://%s?authip=%s" % (link, request.META['REMOTE_ADDR'])
	#print url
	#opener = urllib.FancyURLopener(key_file=key, cert_file=cert)
	#conn = opener.open(url)
	#redirect_url = conn.geturl()
	#print redirect_url
	#return HttpResponseRedirect(redirect_url)



	# load dynamic engine
	e = Engine.load_dynamic_engine("pkcs11", "/usr/local/lib/engine_pkcs11.so")

	pk = Engine.Engine("pkcs11")
	pk.ctrl_cmd_string("MODULE_PATH", "/usr/lib/libeTPkcs11.so")
	ret = pk.init()
	
	if link.startswith("eunode4"):
		#China Relics certificates
		print "Loading certificate China Relics"
        	cert = e.load_certificate("46454335374537413032383233464631")
        	print "Loading key China Relics ..."
		key = e.load_private_key("46454335374537413032383233464631", "indicate#2011")
	else:
		print "Loading certificate DeRoberto"
		cert = e.load_certificate("30354530383037334131344144353636")
		print "Loading key DeRoberto ..."
		key = e.load_private_key("30354530383037334131344144353636", "indicate#2011")

	
	
	ctx = SSL.Context("sslv23")
	ctx.set_cipher_list("HIGH:!aNULL:!eNULL:@STRENGTH")
	ctx.set_session_id_ctx("foobar")
	m2.ssl_ctx_use_x509(ctx.ctx, cert.x509)
	m2.ssl_ctx_use_pkey_privkey(ctx.ctx, key.pkey)

	class SmartRedirectHandler(m2urllib2.HTTPRedirectHandler):
		def http_error_302(self, req, fp, code, msg, headers):
        		redirect = headers['Location']
			return redirect

	opener = m2urllib2.build_opener(ctx, SmartRedirectHandler())
	#m2urllib2.install_opener(opener)
	
	print link
	link = "https://%s?authip=%s" % (link, request.META['REMOTE_ADDR'])	
	print "link: ", link
	req = m2urllib2.Request(str(link))
	redirect_url = opener.open(req)

	#redirect_url = u.geturl()
	
	print redirect_url
	
	pk.finish()                                   
	Engine.cleanup()
	
	return HttpResponseRedirect(redirect_url)

# Returns a Json data structure with information of the directory /medrepo/Entries/Scans
# that allows to construct the columns of a grid panel in ExtJS
# Testing/learning purposes
def columnas(request,repo):
	client=mdclient.MDClient('glibrary.ct.infn.it',8822,'miguel','p1pp0')
	directory='/'+repo+'/Entries/Scans'
	client.selectAttr(['/'+repo+'/Types:VisibleAttrs','ColumnWidth','ColumnLabels'],'Path="'+directory+'"')
	entry=client.getSelectAttrEntry()
	visAttrs=entry[0].split(' ')
	print visAttrs
	atr,types=client.listAttr(directory)
	fields=[]
	columns=[]
	if request.method != 'OPTIONS':
		for i in range(len(atr)):
			fields.append({'name': atr[i], 'mapping': atr[i]})
			columns.append({'header': atr[i], 'width': 30, 'dataIndex': atr[i], 'colType': types[i]})
	jsonData= json.dumps({'metadata':{'root': 'records','totalProperty': 'total','fields': fields},'columns': columns})
	html = "%s" % jsonData
	response=HttpResponse(html)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response


#@csrf_exempt
def addEntry(request, repo, type):
        print "sono in addEntry"
        print request.POST
	#print request.POST.keys()
	#print request.POST.values()
	#print request.POST.iterlists()
	results = {}
	for k, v in request.POST.iterlists():
		results[k] = v[0].encode()
	results['SubmissionDate'] = str(datetime.datetime.now())[:16]
	results['Thumb'] = 1
	print results.keys()
	print results.values()

        
        client=mdclient.MDClient('glibrary.ct.infn.it',8822,'aginfra','4g1nfr4')
        entry_id = client.sequenceNext('/' + repo + '/Entries/id')
        client.addEntry('/' +  repo + '/Entries/' + type + '/' + entry_id, results.keys(), results.values())
                #c['cid'] = cid 

        success = {'success': True, 'data': results}
        response=HttpResponse(json.dumps(success))
        #response=HttpResponse(request.raw_post_data)
	response['Access-Control-Allow-Origin']='*'
        response['Access-Control-Allow-Methods']='GET,POST'
        response['Access-Control-Allow-Headers']='x-requested-with'
        return response

@csrf_exempt
def saveMetadata(request, repo, path):
	print "sono in saveMetadata"
	print "repo:", repo
	print "path:", path
	print request.POST
	print "method:", request.method

	#print request.POST.keys()
	#print request.POST.values()
	#print request.POST.iterlists()
	results = {}
	if request.method != 'OPTIONS':
		for k, v in request.POST.iterlists():
			results[k] = v[0].encode()
		results['SubmissionDate'] = str(datetime.datetime.now())[:16]
		results['Thumb'] = 0
		surl = results['Replica']
		results.pop('Replica', None)
		print results.keys()
		print results.values()

		client=mdclient.MDClient('glibrary.ct.infn.it',8822,'glibraryadmin','r3p0@dm1N')
		entry_id = client.sequenceNext('/' + repo + '/Entries/id')
		client.addEntry('/' +  repo + '/' + path + '/' + entry_id, results.keys(), results.values())
		#c['cid'] = cid 
		rep_id = client.sequenceNext('/' + repo + '/Replicas/rep')
		client.addEntry('/' + repo + '/Replicas/' + rep_id, ['surl', 'ID', 'enabled'], [surl, entry_id, True])

	success = {'success': True, 'data': results}
	response=HttpResponse(json.dumps(success))
	#response=HttpResponse(request.raw_post_data)
	response['Access-Control-Allow-Origin']='*'
	response['Access-Control-Allow-Methods']='GET,POST'
	response['Access-Control-Allow-Headers']='x-requested-with'
	return response


def print_env(request):
	print request.META
	return HttpResponse(request.META)

def convert_time(request,time):
	print type(time), time
	return HttpResponse(datetools.getDateFromTimeIndex(int(time)))	

def retrieve_index(request, date):
	print date
	return HttpResponse(datetools.getTimeIndexFromDate(date))
 
