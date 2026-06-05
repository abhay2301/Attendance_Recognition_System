from django import forms
from .models import FaceImage, Person, RecognitionLog

class FaceImageUploadForm(forms.ModelForm):
    """Form for uploading face images"""
    class Meta:
        model = FaceImage
        fields = ['image', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png',
                'required': True
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'image': 'Upload Face Image',
            'is_primary': 'Set as Primary Image'
        }
        help_texts = {
            'image': 'Upload a clear, front-facing photo of your face (JPG, JPEG, or PNG)',
            'is_primary': 'Mark this as your main face image for recognition'
        }

class PersonForm(forms.ModelForm):
    """Form for creating/updating person information"""
    class Meta:
        model = Person
        fields = ['name', 'email', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional information (optional)'
            }),
        }

class FaceRecognitionForm(forms.Form):
    """Form for face recognition testing"""
    image = forms.ImageField(
        label='Upload Image for Recognition',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png'
        }),
        help_text='Upload an image to test face recognition'
    )
    confidence_threshold = forms.FloatField(
        label='Confidence Threshold (%)',
        initial=70.0,
        min_value=0.0,
        max_value=100.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        }),
        help_text='Minimum confidence score required for recognition (0-100)'
    )

class MultipleFaceUploadForm(forms.Form):
    """Form for uploading multiple face images at once"""
    images = forms.ImageField(
        label='Upload Multiple Face Images',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png',
            'multiple': True
        }),
        help_text='Select multiple images (Ctrl+Click or Cmd+Click)',
        required=False
    )
    set_primary = forms.BooleanField(
        label='Set first image as primary',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

class RecognitionLogFilterForm(forms.Form):
    """Form for filtering recognition logs"""
    STATUS_CHOICES = [('', 'All Statuses')] + RecognitionLog.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Status'
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='From Date'
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='To Date'
    )
    min_confidence = forms.FloatField(
        required=False,
        min_value=0.0,
        max_value=100.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'placeholder': 'Min confidence %'
        }),
        label='Minimum Confidence'
    )