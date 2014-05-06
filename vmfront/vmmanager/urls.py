from django.conf.urls import patterns, include, url


urlpatterns = patterns('vmmanager.views',
    # Examples:
    # url(r'^$', 'cloudfront.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'index'),
)
