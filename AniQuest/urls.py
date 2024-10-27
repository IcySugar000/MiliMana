from django.urls import path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

urlpatterns = [
    path('doc/schema/', SpectacularAPIView.as_view(), name='schema'),  # schema的配置文件的路由，下面两个ui也是根据这个配置文件来生成的
    path('doc/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),  # swagger-ui的路由
    path('doc/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),  # redoc的路由
    path('api/bangumi', views.BangumiViewSet.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('api/bangumi/<int:pk>', views.BangumiViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    })),
    path('api/scrape_bangumi/<int:pk>', views.ScrapeBangumiView.as_view()),
    path('api/scrape_bangumi_poster/<int:pk>', views.ScrapeBangumiPosterView.as_view()),
    path('api/config', views.ConfigViewSet.as_view()),
    re_path(r'^.*$', views.index, name='index')
]