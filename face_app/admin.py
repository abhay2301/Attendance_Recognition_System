from django.contrib import admin
from .models import Person, FaceImage, RecognitionLog


class FaceImageInline(admin.TabularInline):
    model = FaceImage
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_by", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [FaceImageInline]


@admin.register(FaceImage)
class FaceImageAdmin(admin.ModelAdmin):
    list_display = (
        "person_id",
        "is_primary",
        "created_at",
    )
    list_filter = ("is_primary", "created_at")
    search_fields = (
        "person_id__name",
        "person_id__email",
    )
    autocomplete_fields = ("person_id",)
    readonly_fields = (
        "id",
        "encoding",
        "created_at",
        "updated_at",
    )


@admin.register(RecognitionLog)
class RecognitionLogAdmin(admin.ModelAdmin):
    list_display = (
        "person_id",
        "status",
        "confidence",
        "timestamp",
    )
    list_filter = ("status", "timestamp")
    search_fields = (
        "person_id__name",
        "person_id__email",
        "ip_address",
    )
    autocomplete_fields = ("person_id",)
    readonly_fields = (
        "id",
        "timestamp",
    )