# forms.py
from django import forms

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(label='Выберите эксель файл (.xlsx)')