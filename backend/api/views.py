# Django import
from django.http import JsonResponse
# Drf import
from rest_framework import generics 
from rest_framework import status

# Custom module import
from .models import Braille, Korean
from .serializers import BrailleSerializer, KoreanSerializer
from angelina_braille import website_recognizer
from tesseract.tesseract_abspath import path as tesseract_path

# Third party modules
import pytesseract
from BrailleToKorean.BrailleToKor import BrailleToKor
from dotenv import load_dotenv
import os

# load .env files
load_dotenv()


class BrailleCreateAPIView(generics.CreateAPIView):
    queryset = Braille.objects.all()
    serializer_class = BrailleSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        img = serializer.data["image"][serializer.data["image"].index("media"):]
        img = os.path.join(os.path.join(os.getcwd(), "backend"), img)
        braille_text = website_recognizer.main(img)
        translator = BrailleToKor()
        text = translator.translation(braille_text)
        
        Braille.objects.get(id=serializer.data["id"]).delete()
        
        return JsonResponse({"text": text}, status=status.HTTP_201_CREATED)
    

class KoreanCreateAPIView(generics.CreateAPIView):
    queryset = Korean.objects.all()
    serializer_class = KoreanSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        img = serializer.data["image"][serializer.data["image"].index("media"):]
        img = os.path.join(os.path.join(os.getcwd(), "backend"), img)
        
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        text = pytesseract.image_to_string(img, lang="kor+eng").replace("\n", " ")
        
        Korean.objects.get(id=serializer.data["id"]).delete()
        
        return JsonResponse({"text": text}, status=status.HTTP_201_CREATED)
    
    
