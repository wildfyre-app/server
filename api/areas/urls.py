from django.urls import path, re_path, include

from . import views


app_name = 'areas'

urlpatterns = [
    # Notifications
    path('notification/', views.NotificationView.as_view(), name='notification'),
    path('<slug:area>/subscribed/', views.SubscribedView.as_view(), name='subscribed'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/subscribe/$', views.SubscribeView.as_view(), name='subscribe'),

    path('', views.AreaView.as_view(), name='areas'),
    path('<slug:area>/', views.QueueView.as_view(), name='queue'),
    path('<slug:area>/own/', views.OwnView.as_view(), name='own'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/(?P<comment>[0-9]+)/$', views.CommentView.as_view(), name='comment'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/spread/$', views.SpreadView.as_view(), name='spread'),

    # Drafts
    path('<slug:area>/drafts/', views.DraftListView.as_view(), name='drafts'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/drafts/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/$', views.DraftDetailView.as_view(), name='draft-detail'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/drafts/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/publish/$', views.PublishDraftView.as_view(), name='draft-publish'),

    # Reputation
    path('<slug:area>/rep/', views.ReputationView.as_view(), name='reputation'),

    # Flags
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/flag/$', views.FlagPostView.as_view(), name='flag'),
    re_path(r'^(?P<area>[-a-zA-Z0-9_]+)/(?P<nonce>[0-9]{8})(?P<pk>[0-9]+)/(?P<comment>[0-9]+)/flag/$', views.FlagCommentView.as_view(), name='flag'),
]
