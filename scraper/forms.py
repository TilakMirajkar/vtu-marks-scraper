from django import forms


class UserInput(forms.Form):
    
    prefix_usn = forms.CharField(
        label='First 7 characters of USN',
        max_length=7,
        widget=forms.TextInput (
            attrs={
                "class": "border border-solid border-slate-300",
                "placeholder": "e.g., 2AG21CS", 
            }
        ))  # first 7 characters of USN


    usn_range = forms.CharField(
        label='USN or Range of USNs',
        max_length=7,
        widget=forms.TextInput (
            attrs={
                "class": "border border-solid border-slate-300",
                "placeholder": "e.g., 1-30", 
            }
        )) # USN range


    sem = forms.IntegerField(
        label='Semester',
        max_value=8,
        widget=forms.NumberInput (
            attrs={
                "class": "border border-solid border-slate-300",
                "placeholder": "e.g., 7", 
            }
        ))  # Semester


    url = forms.CharField(
        label='Results Page URL',
        widget=forms.TextInput (
            attrs={
                "class": "border border-solid border-slate-300",
                "placeholder": "e.g., https://results.vtu.ac.in/JJEcbcs24/index.php", 
            }
        ))   # result page URl
