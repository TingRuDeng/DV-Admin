#coding:utf-8
from django import forms
from jperm.models import *


class EmailForm(forms.ModelForm):
    class Meta:
        model = Email_template

        fields = ['name',
                  'subject',
                  'template_path',
                  # 'to_email',
                  'email_host',
                  'email_port',
                  'email_host_user',
                  'email_host_password']

        # 设置密码表单类型，禁止浏览器自动填充密码
        widgets = {
            'email_host_password': forms.DateInput(attrs={"type": "password", "autocomplete": "new-password"}),
            'to_email': forms.Select(attrs={"class": "chosen-select form-control m-b", "multiple": "multiple"})
        }
