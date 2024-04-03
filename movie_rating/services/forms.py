from django import forms

class MovieForm(forms.Form):
    name = forms.CharField(max_length=100)
    genre = forms.CharField(max_length=100)
    rating = forms.CharField(max_length=10)
    release_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    

class RegisterForm(forms.Form):
    name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=11)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    
class RatingForm(forms.Form):
    user_id = forms.CharField(widget=forms.HiddenInput())
    movie_id = forms.CharField(widget=forms.HiddenInput())
    rating = forms.FloatField(widget=forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '5', 'pattern': '^\d+(?:\.\d{1,1})?$'}))

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 0 or rating > 5:
            raise forms.ValidationError("Rating must be between 0 and 5")
        return round(rating, 1)
