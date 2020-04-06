from django.contrib import admin
from focalpoint.models import FocalPoint, Activity, Comment, Attachment, Board, BoardColumn, BoardTemplate, Workgroup, Swatch


class ActivityAdmin(admin.ModelAdmin):
    list_display = ("title", "focal_point", "completed", "priority", "due_date")
    list_filter = ("focal_point",)
    ordering = ("priority",)
    search_fields = ("title",)


class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "date", "snippet")


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("activity", "added_by", "timestamp", "file")
    autocomplete_fields = ["added_by", "activity"]


class BoardPanelInline(admin.TabularInline):
    model = BoardColumn
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ("name", "focal_point")
    inlines = [BoardPanelInline, ]


# Register your models here.
admin.site.register(FocalPoint)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(BoardTemplate)
admin.site.register(Workgroup)
admin.site.register(Swatch)
