from django.urls import path

from . import views

app_name = 'areas'

urlpatterns = [
    # Notifications
    path('notification/', views.NotificationView.as_view(), name='notification'),
    path('<slug:area>/subscribed/', views.SubscribedView.as_view(), name='subscribed'),
    path('<slug:area>/<int:post>/subscribe/', views.SubscribeView.as_view(), name='subscribe'),

    path('', views.AreaView.as_view(), name='areas'),
    path('<slug:area>/', views.QueueView.as_view(), name='queue'),
    path('<slug:area>/own/', views.OwnView.as_view(), name='own'),
    path('<slug:area>/<int:post>/', views.DetailView.as_view(), name='detail'),
    path('<slug:area>/<int:post>/<int:comment>/', views.CommentView.as_view(), name='comment'),
    path('<slug:area>/<int:post>/spread/', views.SpreadView.as_view(), name='spread'),

    # Drafts
    path('<slug:area>/drafts/', views.DraftListView.as_view(), name='drafts'),
    path('<slug:area>/drafts/<int:post>/', views.DraftDetailView.as_view(), name='draft-detail'),
    path('<slug:area>/drafts/<int:post>/img/<int:img>/', views.DraftImageView.as_view(), name='draft-img'),
    path('<slug:area>/drafts/<int:post>/publish/', views.PublishDraftView.as_view(), name='draft-publish'),

    # Reputation
    path('<slug:area>/rep/', views.ReputationView.as_view(), name='reputation'),

    # Flags
    path('<slug:area>/<int:post>/flag/', views.FlagPostView.as_view(), name='flag'),
    path('<slug:area>/<int:post>/<int:comment>/flag/', views.FlagCommentView.as_view(), name='flag'),
]
