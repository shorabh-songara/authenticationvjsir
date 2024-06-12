from rest_framework import serializers
from accounts.models import User
from django.utils.encoding import force_bytes , smart_str , DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode , urlsafe_base64_encode
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator
from accounts.utils  import Util


class UserRegestrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type' : 'password'},write_only=True)
    class Meta:
        model = User
        fields = [ "name" , "mobile_no" ,"email","password" ,"password2"]
        extra_kwargs={
            'password': {'write_only' :True}
        }
# validating password and con password while registration
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length =255 , style ={'input_type': 'email'})
    password = serializers.CharField(style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ['email' , 'password']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id' , 'email' , 'name' , 'mobile_no']


class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(style = {'input_type' : 'password'} , write_only =True)
    password2 = serializers.CharField(style = {'input_type' : 'password'} , write_only =True)
    class Meta:
        fields = ['password' , 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user') # this we take from view file through context 
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        user.set_password(password)
        user.save()
        return attrs
    


class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255 , style = {'input_type' : 'email'})
    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email = email).exists():
            user = User.objects.get(email = email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('encoded uid ' , uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('password reset token' , token)
            reset_link = f"http://localhost:3000/api/user/reset/{uid}/{token}/"
            print('password reset link' , reset_link)
            # send email
            body = 'click the link for reset your password' + reset_link

            data = {
                'subject' : 'Reset Your Password',
                'body' : body ,
                'to_email' : user.email
            }
            Util.send_mail(data)
            return attrs
        else:
            raise serializers.ValidationError("User with this email does not exist.")
        
class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(style = {'input_type' : 'password'} , write_only =True)
    password2 = serializers.CharField(style = {'input_type' : 'password'} , write_only =True)
    class Meta:
        fields = ['password' , 'password2']

    def validate(self, attrs):
            
     try:
        password = attrs.get('password')
        password2 = attrs.get('password2')
        uid = self.context.get('uid') # this we take from view file through context 
        token = self.context.get('token') # this we take from view file through context 
        if password != password2:
            raise serializers.ValidationError("Passwords do not match.")
        id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id = id)
          # Create an instance of PasswordResetTokenGenerator
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user , token):
            raise serializers.ValidationError("token is not valid or expired")
        user.set_password(password)
        user.save()
        return attrs    
     except DjangoUnicodeDecodeError as identifier:
        PasswordResetTokenGenerator().check_token(user , token)
        raise serializers.ValidationError("token is not valid or expired")
     

class StudentClassSelectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['is_class_11th', 'is_class_12th', 'is_dropper']

    def validate(self, data):
        is_class_11th = data.get('is_class_11th', False)
        is_class_12th = data.get('is_class_12th', False)
        is_dropper = data.get('is_dropper', False)

        selected_classes = [is_class_11th, is_class_12th, is_dropper]
        if sum(selected_classes) != 1:
            raise serializers.ValidationError("Only one class can be selected at a time.")
        return data
        

     