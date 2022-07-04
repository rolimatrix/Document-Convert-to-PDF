# coding=utf-8
from flask_restful import Resource
from http import HTTPStatus
from app.conf import _init_logging
import time


#init logging
logger= _init_logging('ressource.health')

class Health(Resource):
    def get (self):
        logger.info("Post Call for Health started at {}".format(time.asctime(time.localtime(time.time()))))
        return HTTPStatus.OK