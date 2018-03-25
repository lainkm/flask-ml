from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField, PasswordField, StringField,validators
from model import *

class LoginForm(Form):
    id = StringField('id', [
    	validators.InputRequired("请输入正确的用户名")
    ])
    pw = PasswordField('pw', [validators.InputRequired()])
    

    def validate(self):
        if not Form.validate(self):
            return False
        user = query_user(self.name.data)
        if user is None:
            self.name.errors.append('用户名不存在！')
            return False
        if user.pw != self.pw.data:
            self.pw.errors.append('密码错误！')
            return False
        return True

