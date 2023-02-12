from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from .tasks import send_activation_code, send_mentor_activation_code


User = get_user_model()



def email_validator(email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'User with this email does not exist'
            )
        return email



class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class MentorRegistrationSerialiser(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=128, required=True)


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'type_of_teach', 'experience', 'audience', 'password', 'password_confirm')
  

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Email already in use'
            )
        return email


    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        send_mentor_activation_code.delay(user.email, user.activation_code)
        return user

class UserRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(max_length=128, required=True)


    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'password_confirm')


    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Email already in use'
            )
        return email


    def validate(self, attrs):
        password = attrs.get('password')
        password_confirm = attrs.pop('password_confirm')
        if password != password_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.create_activation_code()
        send_activation_code.delay(user.email, user.activation_code)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, required=True)
    new_password = serializers.CharField(max_length=128, required=True)
    new_pass_confirm = serializers.CharField(max_length=128, required=True)

    def validate_old_password(self, old_password):
        user = self.context.get('request').user
        if not user.check_password(old_password):
            raise serializers.ValidationError(
                'Wrong password'
            )
        return old_password
    
    def validate(self, attrs: dict):
        new_password = attrs.get('new_password')
        new_pass_confirm = attrs.get('new_pass_confirm')
        if new_password != new_pass_confirm:
            raise serializers.ValidationError('Passwords do not match')
        return attrs

    def set_new_password(self):
        user = self.context.get('request').user
        password = self.validated_data.get('new_password')
        user.set_password(password)
        user.save()


class RestorePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        max_length=255, 
        validators=[email_validator]
        )

    def send_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        send_mail(
            subject='Password restore',
            message=f'Your code for password restore {user.activation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )

    def send_email_code(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        user.create_activation_code()
        send_mail(
            subject='Change email',
            message=f'Your code for ghange email {user.activation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email]
        )


class SetRestoredPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True, 
        max_length=255,
        validators=[email_validator]
        )
    code = serializers.CharField(min_length=1, max_length=8, required=True)
    new_password = serializers.CharField(max_length=128, required=True)
    new_pass_confirm = serializers.CharField(max_length=128, required=True)

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError(
                'Wrong code'
            )
        return code

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        new_pass_confirm = attrs.get('new_pass_confirm')
        if new_password != new_pass_confirm:
            raise serializers.ValidationError(
                'Passwords do not match'
            )
        return attrs
        
    def set_new_password(self):
        email = self.validated_data.get('email')
        user = User.objects.get(email=email)
        new_password = self.validated_data.get('new_password')
        user.set_password(new_password)
        user.activation_code = ''
        user.save()


class UpdateUsernameImageSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        user = self.context['request'].user
        attrs['user'] = user
        return attrs

    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    def update(self, instance: User, validated_data):
        if instance.email == validated_data['user'].email:
            instance.first_name = validated_data.get('first_name', instance.first_name) 
            instance.last_name = validated_data.get('last_name', instance.last_name) 
            instance.save()
        else:
            raise serializers.ValidationError('Вы не можете совершить это действие!')


class UpdateEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['old_email', 'new_email', 'new_email_confirm', 'code']

    old_email = serializers.EmailField(
        required=True, 
        max_length=255,
        validators=[email_validator]
        )
    new_email = serializers.EmailField(
        required=True, 
        max_length=255,
        )
    new_email_confirm = serializers.EmailField(
        required=True, 
        max_length=255,
        )
    code = serializers.CharField(min_length=1, max_length=8, required=True)
 

    def validate_code(self, code):
        if not User.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError(
                'Wrong code'
            )
        return code
    

    def validate(self, attrs):
        new_email = attrs.get('new_email')
        new_email_confirm = attrs.get('new_email_confirm')
        if new_email != new_email_confirm:
            raise serializers.ValidationError(
                'Email do not match'
            )
        return attrs


    def update(self):
        old_email = self.validated_data.get('old_email')
        new_email = self.validated_data.get('new_email')
        user_email = User.objects.get(email=old_email)
        user_email.email = new_email
        user_email.save()
