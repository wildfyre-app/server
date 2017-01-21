from django.conf.urls import url, include


app_name = 'fun'
package = 'areas.fun'

urlpatterns = [
    url(r'^posts/', include(package + '.posts.urls'), name='posts'),
    url(r'^rep/', include(package + '.rep.urls'), name='rep'),
]
