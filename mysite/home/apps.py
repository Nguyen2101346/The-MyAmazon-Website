from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'
    verbose_name = "🛒 Quản lý cửa hàng"
    def ready(self):
        import home.signals