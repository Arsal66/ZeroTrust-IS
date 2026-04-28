from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
from django.shortcuts import HttpResponse, HttpResponseRedirect, render, redirect
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import User, ClassificationResult, LoginOTP
from ZeroHate.forms import CustomAuthenticationForm, UserCreationForm
from django.views.generic.edit import CreateView
from django.views import View
from django.urls import reverse_lazy
import os, re, string
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import login as auth_login
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import base36_to_int
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
import random
import string
from django.core.mail import BadHeaderError
from django.core.cache import cache











# Load model and tokenizer once at the beginning
model_path = 'ZeroHate/DistilBERT_Model/Trained_Model'  # Update this with the correct path
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Load model to the appropriate device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Clean the input text
def clean_text(text):
    text = text.lower()
    text = text.replace('\\n', ' ')
    text = text.replace('\n', ' ')
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'<.*?>', '', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def classify_text(text):
    # Preprocess the text
    text = clean_text(text)
    
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Move tensors to the appropriate device
    inputs = {key: value.to(device) for key, value in inputs.items()}
    
    # Perform inference without calculating gradients
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    
    # Convert logits to probabilities using sigmoid activation function
    scores = torch.sigmoid(logits).squeeze().tolist()

    # Return the results (probabilities for each label)
    return {
        'toxic': scores[0],
        'severe_toxic': scores[1],
        'obscene': scores[2],
        'threat': scores[3],
        'insult': scores[4],
        'identity_hate': scores[5]
    }


@csrf_exempt  # To handle CSRF token in AJAX requests
@require_POST
def classify_text_view(request):
    key = f"rl:{request.user.id}"
    # try to create with TTL; if it exists, increment
    if not cache.add(key, 1, 60):
        count = cache.incr(key)
    else:
        count = 1
    if count > 5:
        return JsonResponse({'error': 'Rate limit exceeded.'}, status=429)
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text:
            return JsonResponse({'error': 'No text provided'}, status=400)
        
        encrypted_text = encrypt_text(text)
        
        # Call the AI model to classify the text
        scores = classify_text(text)
        # Save to database
        if request.user.is_authenticated:
            ClassificationResult.objects.create(
                user=request.user,
                input_text=encrypted_text,
                toxic=scores['toxic'],
                severe_toxic=scores['severe_toxic'],
                obscene=scores['obscene'],
                threat=scores['threat'],
                insult=scores['insult'],
                identity_hate=scores['identity_hate'],
            )

        # Return the results as JSON
        return JsonResponse({
            'text': text,
            'toxic': scores['toxic'],
            'severe_toxic': scores['severe_toxic'],
            'obscene': scores['obscene'],
            'threat': scores['threat'],
            'insult': scores['insult'],
            'identity_hate': scores['identity_hate'],
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard(request):
    """
    Dashboard view displaying the main text classification interface
    """
    # Fetch recent classifications, limit to the last 5 or 10
    recent_classifications = ClassificationResult.objects.filter(user=request.user).order_by('-created_at')[:10]
    for obj in recent_classifications:
        try:
            obj.input_text = decrypt_text(obj.input_text)
        except Exception:
            obj.input_text = "[decryption failed]"

    return render(request, 'ZeroHate/dashboard.html', {
        'recent_classifications': recent_classifications
    })


def confirmation_sent(request):
    return render(request, 'ZeroHate/confirmation_sent.html')



class TwoMinuteTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"

    def check_token(self, user, token):
        # Let Django validate the token structure first
        if not super().check_token(user, token):
            print("Invalid token structure")
            return False

        try:
            ts_b36 = token.split("-")[0]  # First part is the timestamp in Django token
            ts_int = base36_to_int(ts_b36)
            current_time = self._num_seconds(datetime.now())
            token_time = ts_int  # Already in seconds
            # Convert the base36 timestamp to seconds since 2001-01-01
            token_age = current_time - token_time  # Calculate the token's age

            # Check if the token age is within the allowed expiration time (e.g., 1 minute)
            return token_age <= 120 # 2 minutes
        except Exception as e:
            print("Token check error:", e)
            return False


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    token_generator = TwoMinuteTokenGenerator()

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True  # Activate user
        user.save()
        auth_login(request, user)  # Log the user in
        return render(request, 'ZeroHate/account_activated.html')
    else:
        return HttpResponse('Activation link is invalid!')


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            # Email verification logic
            token_generator = TwoMinuteTokenGenerator()
            token = token_generator.make_token(user)

            uid = urlsafe_base64_encode(force_bytes(user.pk))

            subject = "Confirm your email"
            html_message = render_to_string('ZeroHate/verification_email.html', {
                'user': user,
                'domain': request.get_host(),
                'uidb64': uid,
                'token': token,
            })
            plain_message = strip_tags(html_message)

            email = form.cleaned_data.get('email')
            email_message = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

            return render(request, 'ZeroHate/confirmation_sent.html')  # confirmation page
        else:
            messages.warning(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'ZeroHate/signup.html', {'form': form})



# views.py
def verify_otp(request):
    if request.method == 'POST':
        # Capture the OTP inputted by the user
        input_otp = ''.join([request.POST.get(f'otp{i}', '') for i in '123456'])
        
        # Get user from session
        user_id = request.session.get('pre_otp_user_id')
        
        try:
            user = User.objects.get(id=user_id)
            
            # Fetch the OTP record for the user
            record = LoginOTP.objects.get(user=user)
            
            # Check if the OTP matches and is within the time limit
            if record.otp == input_otp and timezone.now() - record.created_at <= timedelta(minutes=2):
                auth_login(request, user)  # Log the user in
                return redirect('dashboard')  # Redirect to the dashboard
            else:
                messages.error(request, "Invalid or expired OTP.")  # Invalid OTP or expired
        except LoginOTP.DoesNotExist:
            messages.error(request, "OTP record does not exist.")  # If no OTP record exists
        except Exception as e:
            messages.error(request, f"OTP validation failed: {str(e)}")  # Other errors

    return render(request, 'ZeroHate/verify_otp.html')



def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if user is not None and user.is_active:
                is_first_login = not LoginOTP.objects.filter(user=user).exists()
                login_counts = 0
                if not is_first_login:
                    previous_otp = LoginOTP.objects.get(user=user)
                    login_counts = previous_otp.login_counts
                if is_first_login or login_counts >= 5:
                    print(login_counts)

                    # Generate 6-character OTP with uppercase letters and digits
                    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

                    # Save or update OTP for user
                    LoginOTP.objects.update_or_create(user=user, defaults={'otp': otp, 'login_counts': 1, 'created_at': timezone.now()})

                    subject = "Your Login OTP"
                    html_message = render_to_string('ZeroHate/otp_email.html', {
                        'user': user,
                        'otp': otp,
                        'validity': '2 minutes'
                    })
                    plain_message = strip_tags(html_message)

                    # Send email
                    email = user.email
                    email_message = EmailMultiAlternatives(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email])
                    email_message.attach_alternative(html_message, "text/html")
                    try:
                        email_message.send()
                        print("Email sent successfully!")
                    except BadHeaderError:
                        print("Invalid header found.")
                    except Exception as e:
                        print(f"Error sending email: {e}")
                        
                    # Redirect to OTP verification page
                    request.session['pre_otp_user_id'] = user.id
                    return redirect('verify_otp')
                else:
                    # Update OTP for user
                    LoginOTP.objects.filter(user=user).update(login_counts=login_counts+1, created_at=timezone.now())
                    auth_login(request, user)  # Log the user in
                    return redirect('dashboard')  # Redirect to the dashboard
            else:
                messages.warning(request, 'Your account is inactive. Please verify your email.')
        else:
            messages.warning(request, 'Invalid login credentials.')

    return render(request, 'ZeroHate/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login') 


import os
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from PyPDF2 import PdfReader
import docx

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or '' for page in reader.pages)
    elif ext == '.docx':
        doc = docx.Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        return "Unsupported file format"

def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(f"ZeroHate/Files/{uploaded_file.name}", uploaded_file)
        file_path = fs.path(filename)

        file_text = extract_text_from_file(file_path)
        cleaned_text = clean_text(file_text)
        return JsonResponse({'message': 'File uploaded successfully', 'text': cleaned_text})
    return JsonResponse({'error': 'No file uploaded'}, status=400)






















from cryptography.fernet import Fernet
import base64

# Assume the key is securely stored in your settings (e.g., settings.py or environment variable)
# For demonstration, we generate the key here, but you should replace it with a securely stored key.
key = os.getenv('FERNET_KEY')
cipher = Fernet(key)

# Function to encrypt text
def encrypt_text(plain_text):
    encrypted_text = cipher.encrypt(plain_text.encode())  # Encrypting the text
    # Convert the encrypted bytes to a base64 string for JSON serialization
    encrypted_text_base64 = base64.b64encode(encrypted_text).decode('utf-8')
    return encrypted_text_base64

# Function to decrypt text
def decrypt_text(encrypted_text_base64):
    # Decode the base64 string back to bytes
    encrypted_text = base64.b64decode(encrypted_text_base64.encode('utf-8'))
    decrypted_text = cipher.decrypt(encrypted_text).decode()  # Decrypting the text
    return decrypted_text