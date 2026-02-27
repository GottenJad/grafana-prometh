from flask import jsonify
import time
import platform
import psutil 
from app import app
from app.extensions import db, cache

@app.route('/health')
def health():
    """Health check endpoint с расширенной информацией"""
    health_data = {
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'flask-app',
        'version': '1.0.0',
        'checks': {
            'database': check_database(),
            'cache': check_cache(),
            'disk': check_disk_space(),
            'memory': check_memory()
        }
    }
    
    # Определяем общий статус
    all_healthy = all(check['status'] == 'healthy' 
                     for check in health_data['checks'].values())
    health_data['status'] = 'healthy' if all_healthy else 'degraded'
    
    return jsonify(health_data)

def check_database():
    """Проверка подключения к БД"""
    try:
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'message': 'Database connection OK'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def check_cache():
    """Проверка подключения к Redis"""
    try:
        cache.get('health_check')
        return {'status': 'healthy', 'message': 'Cache connection OK'}
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def check_disk_space():
    """Проверка свободного места на диске"""
    try:
        disk = psutil.disk_usage('/')
        free_percent = (disk.free / disk.total) * 100
        return {
            'status': 'healthy' if free_percent > 10 else 'warning',
            'free_percent': free_percent,
            'total_gb': disk.total / (1024**3),
            'free_gb': disk.free / (1024**3)
        }
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}

def check_memory():
    """Проверка использования памяти"""
    try:
        memory = psutil.virtual_memory()
        return {
            'status': 'healthy' if memory.percent < 90 else 'warning',
            'percent_used': memory.percent,
            'total_gb': memory.total / (1024**3),
            'available_gb': memory.available / (1024**3)
        }
    except Exception as e:
        return {'status': 'unhealthy', 'message': str(e)}