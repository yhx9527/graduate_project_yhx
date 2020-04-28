from app import server
from celery_app.tasks import crawling, gen_model_task
from flask import jsonify, request
# from diggout.user_similar import gen_model, gen_MatrixSimilarity
from config import API_PWD

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
            'nickname': '',
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'end': task.info.get('end', 1),
            'result': task.info.get('result', []),
            'status': task.info.get('status', ''),
            'id': task.info.get('id', 0),
            'cur': task.info.get('cur', 0),
            'nickname':task.info.get('nickname', '')
        }
    else:
        # something went wrong in the background job
        response = {
            'id': -1,
            'state': task.state,
            'end': 1,
            'result': [],
            'cur': 0,
            'nickname': '',
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@server.route('/gen_model')
def api_gen_d2v():
    pwd = request.args.get('pwd')
    model = request.args.get('model')
    print('获取生成模型需要的密码', pwd, model)
    if pwd == API_PWD:
        # if model == 'd2v':
        #     gen_model()
        # elif model == 'sim':
        #     gen_MatrixSimilarity()
        # else:
        #     return '模型参数不正确'
        # return '模型生成完成'
        if model in ['d2v', 'sim']:
            gen_model_task.apply_async(args=[model])
            return '已开启模型生成任务'
        else:
            return '模型参数不正确'

    else:
        return '暗号不正确～'



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
