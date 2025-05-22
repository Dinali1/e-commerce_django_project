from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ValidationError
from django.forms import Form, CharField, ModelForm, PasswordInput, EmailField
from redis import Redis

from apps.models import User, Stream, Payment


class EmailForm(Form):
    email=CharField(max_length=255)

    def clean_email(self):
        email=self.cleaned_data.get('email')
        return email

# class RegisterModelForm(ModelForm):
#     code=CharField(max_length=20)
#     class Meta:
#         model=User
#         fields=['email']
    # def clean_code(self):
    #     code = self.cleaned_data.get('code')
    #     email = self.data.get('email')
    #     return email


class LoginForm(Form):
    email = CharField(max_length=100)
    password = CharField(max_length=100)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        query = User.objects.filter(email=email)
        if not query.exists():
            raise ValidationError(f'{email} is not exists')
        user = query.first()
        if not check_password(password, user.password):
            raise ValidationError('Password error')
        self.user = user
        return super().clean()

class ProfileModelForm(ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class PhoneNumberForm(ModelForm):
    class Meta:
        model = User
        fields = ['phone_number']

class PasswordForm(ModelForm):
    confirm_password = CharField(max_length=100)
    class Meta:
        model = User
        fields = ['password']

    def clean(self):
        cleaned_data = super().clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError('Passwords do not match')
        cleaned_data['password'] = make_password(password)
        return cleaned_data

class SaveStreamForm(ModelForm):
    class Meta:
        model = Stream
        fields = ['name', 'is_established', 'product']

class PaymentModelForm(ModelForm):
    class Meta:
        model = Payment
        fields = 'amount', 'card_number', 'user'

    def clean_payment_amount(self):
        user_id = self.data.get('user')
        pay_amount = self.cleaned_data.get('amount')
        user = User.objects.get(pk=user_id)
        if user.balance < pay_amount:
            raise ValidationError(f"Balance da pul yetarli emas")
        return pay_amount
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')
        if not card_number.isdigit():
            raise ValidationError('Write only numbers except letters')
        return card_number








