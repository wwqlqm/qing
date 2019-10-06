from flask import request
from flask import g
from flask import Blueprint
from utils.base import BaseResponse
from config.config import db

api_bp = Blueprint('bk', __name__)

@api_bp.route('/index')
def get_bk():
    a = 1
    return BaseResponse.return_success(a)
