import os
from celery import Celery

# задаем переменную окружения DJANGO_SETTINGS_MODULE для консольных команд Celery.
os.environ.setdefault('DJANGO_SETTING_MODULE', 'core.settings')

# создаем экземпляр приложения
app = Celery('core')

# загружаем конфигурацию из настроек нашего проекта, вызывая метод
# config_from_object(). Параметр namespace определяет префикс, который
# мы будем добавлять для всех настроек, связанных с Celery. Таким
# образом, в файле settings.py можно будет задавать конфигурацию Celery
# через настройки вида CELERY_, например CELERY_BROKER_URL;
app.config_from_object('django.conf:settings', namespace='CELERY')

# вызываем процесс поиска и загрузки асинхронных задач по
# нашему проекту. Celery пройдет по всем приложениям, указанным в
# настройке INSTALLED_APPS, и попытается найти файл tasks.py, чтобы
# загрузить код задач
app.autodiscover_tasks()


