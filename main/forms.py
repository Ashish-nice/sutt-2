from django import forms

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(
        widget=forms.FileInput(attrs={'accept': '.xls, .xlsx'}),
        label="Upload Excel File",
    )
