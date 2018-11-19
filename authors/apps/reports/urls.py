from django.urls import path

from .views import ReportAPIView, ReportListAPIView, ReportActionsAPIView, ReportListUserAPIView

urlpatterns = [
    path('articles/reports/my_reports',
         ReportListUserAPIView.as_view(), name='report_user_list'),
    path('articles/<slug>/report', ReportAPIView.as_view(), name='report'),
    path('articles/reports/all', ReportListAPIView.as_view(), name='report_list'),
    path('articles/reports/<pk>',
         ReportActionsAPIView.as_view(), name='report_delete'),
]
