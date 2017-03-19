from django.conf.urls import url, include

from . import views


app_name = 'areas'

urlpatterns = [
    url(r'^$', views.AreaView.as_view(), name='areas'),
    url(r'^(?P<area>[a-z]*)/$', views.QueueView.as_view(), name='queue'),
    url(r'^(?P<area>[a-z]*)/own/$', views.OwnView.as_view(), name='own'),
    url(r'^(?P<area>[a-z]*)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<area>[a-z]*)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/(?P<comment>[0-9]+)/$', views.CommentView.as_view(), name='comment'),
    url(r'^(?P<area>[a-z]*)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/spread/(?P<spread>0|1)/$', views.SpreadView.as_view(), name='spread'),

    url(r'^(?P<area>[a-z]*)/rep/$', views.ReputationView.as_view(), name='reputation'),
]
