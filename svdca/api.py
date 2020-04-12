from app import server
from celery_app.tasks import crawling
from flask import jsonify
@server.route('/status/<task_id>')
def taskstatus(task_id):
    task = crawling.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'end': 0,
            'result': [],
            'status': '爬虫启动中...',
            'id': 0,
            'cur': 0,
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'end': task.info.get('end', 1),
            'result': task.info.get('result', []),
            'status': task.info.get('status', ''),
            'id': task.info.get('id', 0),
            'cur': task.info.get('cur', 0),
        }
    else:
        # something went wrong in the background job
        response = {
            'id': -1,
            'state': task.state,
            'end': 1,
            'result': [],
            'cur': 0,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

# @server.route('/similar_status/<task_id>')
# def similar_tatus(task_id):
#     task = task_get_similar.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {
#             'state': task.state,
#             'end': 0,
#             'result': '',
#             'status': '启动用户相似分析...',
#             'id': 0,
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'end': task.info.get('end', 0),
#             'result': task.info.get('result', ''),
#             'status': task.info.get('status', ''),
#             'id': task.info.get('id', 0),
#         }
#     else:
#         # something went wrong in the background job
#         response = {
#             'id': -1,
#             'state': task.state,
#             'end': 1,
#             'result': [],
#             'status': str(task.info),  # this is the exception raised
#         }
#     return jsonify(response)
