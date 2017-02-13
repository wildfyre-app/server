from django.conf.urls import url, include

from . import views

app_name = 'posts'

urlpatterns = [
    url(r'^$', views.PostView.as_view(), name='post'),
    url(r'own/$', views.OwnView.as_view(), name='own'),
    url(r'(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/(?P<comment>[0-9]+)/$', views.CommentView.as_view(), name='comment'),
    url(r'(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/(?P<spread>0|1)/$', views.SpreadView.as_view(), name='spread'),
]
