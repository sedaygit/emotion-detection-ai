from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files import File
from . forms import CreateUserForm, LoginForm, ImageUploadForm, ResultForm
from .models import UploadedImage, AnalysisResult
from ultralytics import YOLO
import requests
import yaml
import os
import uuid

#authentication models
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required

from django.http import HttpResponse 
#kullanıcıya bi yanıt nesnesi döndürülmesini sağlar

#view sayfa içeriğini URLconf içeriğin yerini belirler
#view çağırmak için url ile haritalandırmak gerekir

def homepage(request):
    return render(request, 'emotiondetection/index.html')


def register(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)

        if form.is_valid():
            form.save()

            return redirect("my-login")
        
    context = {'registerform': form}  
    #register.html is based on context dictionary

    return render(request, 'emotiondetection/register.html', context=context)


def my_login(request):
    form = LoginForm()

    if request.method == 'POST' :
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth.login(request, user)

                return redirect("dashboard")
            
    context = {'loginform': form}        

    return render(request, 'emotiondetection/my-login.html', context=context)


#@login_required(login_url="my-login") #security for direct enter to dashboard
def dashboard(request):
    user = request.user
    if user.is_authenticated:
        uploaded_images = UploadedImage.objects.filter(registered_user=user)
    else:
        uploaded_images = []
    context = {
        'uploaded_images': uploaded_images,
    }
    return render(request, 'emotiondetection/dashboard.html', context)

@login_required(login_url="register")
def user_analysis_results(request):
    user = request.user
    if user.is_authenticated:
        analysis_results = AnalysisResult.objects.filter(detected_image__registered_user=user).order_by('-date_time')
    else:
        analysis_results = []    

    return render(request, 'emotiondetection/previous.html', {'analysis_results': analysis_results})


def user_logout(request):
    auth.logout(request)
    return redirect("") #boş olduğu için anasayfaya yönlendirir


def handle_upload(request):
    form = ImageUploadForm()
    resultForm = ResultForm()
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            uploaded_image.registered_user = request.user if request.user.is_authenticated else None
            uploaded_image.save()

            image_path = uploaded_image.image.path

            unique_id = uuid.uuid4()
            output_dir = os.path.join('runs', 'detect', 'predict', str(unique_id).replace('-',''))
            os.makedirs(output_dir, exist_ok=True)

            model_face = YOLO("yolov8n-face.pt")
            detected_face = model_face.predict(image_path, save=True, save_crop=True, project=output_dir)

            cropped_faces_dir = os.path.join(output_dir, 'predict', 'crops', 'face')
            detect_emotions(cropped_faces_dir, output_dir)

            image_display_path = os.path.join(output_dir, 'predict2')
            image_display_file = os.listdir(image_display_path)[0]
            image_display_path = os.path.join(image_display_path, image_display_file)

            emotions = []
            with open(os.path.join(output_dir, 'confidences.txt'), 'r') as file:
                for line in file:
                    emotions.append(line.strip())

            image_url = os.path.join(settings.MEDIA_URL, 'detect', 'predict', str(unique_id).replace('-', ''), 'predict2', image_display_file)
            #image_url = resultForm.save() 

            result_instance = AnalysisResult(
                detected_image=uploaded_image,
            )
            result_instance.save()


            return render(request, 'emotiondetection/dashboard.html', {'image': image_url, 'emotions': emotions})
        else:
            print(form.errors)

    context={
        "imageform": form,
        "result": resultForm,
    }

    return render(request, 'emotiondetection/dashboard.html', context=context)     


def detect_emotions(cropped_face_dir, output_dir):
    model = YOLO('yolov8n-emo.pt')  # Use the appropriate model variant

# Load class labels from label56.yaml
    with open('label56.yaml', 'r') as file:
        config = yaml.safe_load(file)
        class_labels = config['names']


    for face_image in os.listdir(cropped_face_dir):
        face_image_path = os.path.join(cropped_face_dir, face_image)
        results=model(face_image_path,save=True, project=output_dir)


        # Open a file to save the confidence scores and bounding box information
        with open(os.path.join(output_dir ,'confidences.txt'), 'w') as f:
            for result in results:
                boxes = result.boxes  # This includes both coordinates and confidence scores
                if boxes is not None:
                    boxes_np = boxes.xyxy.cpu().numpy()  # Convert to NumPy array and ensure it's on CPU
                    confidences = boxes.conf.cpu().numpy()  # Extract confidence scores and ensure they're on CPU
                    class_ids = boxes.cls.cpu().numpy()  # Extract class IDs and ensure they're on CPU
                    
                    for box, confidence, class_id in zip(boxes_np, confidences, class_ids):
                        # Convert class_id to integer
                        class_id = int(class_id)
                        # Format the confidence to four decimal places
                        formatted_confidence = f"{confidence:.4f}"
                        # Get the corresponding emotion label
                        emotion_label = class_labels.get(class_id, "unknown")
                        # Write to the file without class ID
                        f.write(f"Box: {box}, Confidence: {formatted_confidence}, Emotion: {emotion_label}\n")
                        # Print to console
                        print(f"Box: {box}, Confidence: {formatted_confidence}, Emotion: {emotion_label}")  

