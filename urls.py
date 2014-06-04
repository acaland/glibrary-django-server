#from django.conf.urls.defaults import *
from django.conf.urls import patterns, url, include
from gltest.views import *

urlpatterns = patterns('',
    (r'^time/$', current_datetime),
    (r'^convertTime/(?P<time>[0-9]+)/$', convert_time),
    (r'^retrieveIndex/(?P<date>[0-9\-]+)/$', retrieve_index),
    (r'^env/$', print_env),
	(r'^glib/(?P<directory>[a-zA-Z0-9/]+)/$', getData),
	(r'^getTree/$', get_tree),
	(r'^getTree/(?P<tree_id>[a-zA-Z0-9/]+)/$', get_tree_dir),
	(r'^mountTree/(?P<repo>[a-zA-Z0-9/]+)/$',getTree),
	(r'^test/(?P<directory>[a-zA-Z0-9/]+)/$',getFilterValues),
	(r'^data/$',data),
	(r'^metadata/(?P<directory>[a-zA-Z0-9/]+)/$',metadata),
	(r'^links/(?P<repo>[a-zA-Z0-9/]+)/(?P<id>[0-9]+)/$',getLinks),
	(r'^links2/(?P<repo>[a-zA-Z0-9/]+)/(?P<id>[0-9]+)/$',getLinks2),
	(r'^columnas/(?P<repo>[a-zA-Z0-9/]+)/$',columnas),
    (r'^download/(?P<link>[a-zA-Z0-9/.:_-]+)/$',download),
	(r'^addEntry/(?P<repo>[a-zA-Z0-9/_-]+)/(?P<type>[a-zA-Z0-9/_-]+)/$', addEntry),
	(r'^saveMetadata/(?P<repo>[a-zA-Z0-9_-]+)/(?P<path>[a-zA-Z0-9/_-]+)/$', saveMetadata)
)
