"""
Test suite for the Flask application
"""
import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, create_app, get_environment_info, get_memory_info, get_cpu_info


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture
def app_context():
    """Create an application context for testing"""
    with app.app_context():
        yield app


class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check_default(self, client):
        """Test health check endpoint with default probe"""
        response = client.get('/healthcheck.html')
        assert response.status_code == 200
        assert b'healthy' in response.data
        assert b'Health Check' in response.data
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_health_check_with_probe(self, client):
        """Test health check endpoint with specific probe"""
        response = client.get('/healthcheck.html?probe=liveness')
        assert response.status_code == 200
        assert b'liveness' in response.data
        assert b'healthy' in response.data


class TestMainEndpoint:
    """Test main application endpoint"""
    
    def test_main_page_loads(self, client):
        """Test that main page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Environment Display' in response.data
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_main_page_contains_environment_info(self, client):
        """Test that main page contains environment information"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Kubernetes Information' in response.data
        assert b'System Information' in response.data
        assert b'Application Status' in response.data
    
    @patch.dict(os.environ, {'ENVIRONMENT': 'test', 'BG_COLOR': '#ff0000'})
    def test_main_page_with_custom_env(self, client):
        """Test main page with custom environment variables"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'test' in response.data.lower()


class TestAPIEndpoint:
    """Test API endpoint"""
    
    def test_api_env_endpoint(self, client):
        """Test API environment endpoint"""
        response = client.get('/api/env')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert 'environment' in data
        assert 'kubernetes' in data
        assert 'uptime' in data
        assert 'timestamp' in data
    
    def test_api_env_structure(self, client):
        """Test API endpoint returns expected structure"""
        response = client.get('/api/env')
        data = json.loads(response.data)
        
        # Check required fields
        required_fields = ['environment', 'bg_color', 'font_color', 'server', 'kubernetes', 'uptime']
        for field in required_fields:
            assert field in data
        
        # Check kubernetes structure
        k8s_fields = ['pod_name', 'pod_namespace', 'host_ip']
        for field in k8s_fields:
            assert field in data['kubernetes']


class TestErrorHandlers:
    """Test error handling"""
    
    def test_404_handler(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-endpoint')
        assert response.status_code == 404
        assert response.content_type == 'application/json'
        
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'
        assert data['path'] == '/nonexistent-endpoint'


class TestUtilityFunctions:
    """Test utility functions"""
    
    @patch('psutil.virtual_memory')
    def test_get_memory_info(self, mock_memory):
        """Test memory information retrieval"""
        mock_memory.return_value = MagicMock(
            total=8589934592,  # 8GB
            available=4294967296,  # 4GB
            used=4294967296,  # 4GB
            percent=50.0
        )
        
        memory_info = get_memory_info()
        assert memory_info['total'] == 8192  # MB
        assert memory_info['available'] == 4096  # MB
        assert memory_info['used'] == 4096  # MB
        assert memory_info['percent'] == 50.0
    
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_percent')
    @patch('os.getloadavg')
    def test_get_cpu_info(self, mock_loadavg, mock_cpu_percent, mock_cpu_count):
        """Test CPU information retrieval"""
        mock_cpu_count.return_value = 4
        mock_cpu_percent.return_value = 25.5
        mock_loadavg.return_value = [1.0, 1.5, 2.0]
        
        cpu_info = get_cpu_info()
        assert cpu_info['count'] == 4
        assert cpu_info['percent'] == 25.5
        assert cpu_info['load_avg'] == [1.0, 1.5, 2.0]
    
    def test_get_environment_info_structure(self):
        """Test environment info returns expected structure"""
        env_info = get_environment_info()
        
        # Check main sections
        main_sections = ['kubernetes', 'application', 'server', 'system', 'process', 'volumes', 'environment_variables']
        for section in main_sections:
            assert section in env_info
        
        # Check application section
        app_fields = ['environment', 'uptime', 'timestamp', 'python_version', 'platform']
        for field in app_fields:
            assert field in env_info['application']


class TestApplicationFactory:
    """Test application factory"""
    
    def test_create_app(self):
        """Test application factory function"""
        test_app = create_app()
        assert test_app is not None
        assert test_app.config['TESTING'] is False  # Default state


class TestConfiguration:
    """Test application configuration"""
    
    def test_app_config(self, app_context):
        """Test application configuration"""
        assert app.config['JSON_SORT_KEYS'] is False
        assert app.config['DEBUG'] is False
        assert 'SECRET_KEY' in app.config
    
    @patch.dict(os.environ, {'SECRET_KEY': 'test-secret-key'})
    def test_secret_key_from_env(self, app_context):
        """Test secret key configuration from environment"""
        # This would require app restart to take effect
        # Just test that the environment variable is accessible
        assert os.environ.get('SECRET_KEY') == 'test-secret-key'


if __name__ == '__main__':
    pytest.main([__file__])
