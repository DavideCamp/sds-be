from unittest.mock import patch
from celery import Celery


def test_connection_sends_task():
    app = Celery('test', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    with patch('celery.Celery.send_task') as mock_send_task:
        app.send_task('documents.tasks.add', args=[2, 2])
        mock_send_task.assert_called_once_with('documents.tasks.add', args=[2, 2])

def test_connection_returns_true():
    app = Celery('test', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    result = app.send_task('documents.tasks.add', args=[2, 2])
    assert result.get(timeout=10) == 4
    
def test_upload_document():
    app = Celery('test', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')
    res =app.send_task('documents.tasks.process_document', args=[1])
    assert res.get(timeout=10)
    