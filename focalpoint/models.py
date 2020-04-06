import os
import textwrap
import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import models
from django.urls import reverse
from taggit.managers import TaggableManager


def get_attachment_upload_dir(instance, filename):
    """
    Determine upload dir for activity attachment files.
    """
    return "/".join(["activity", "attachments", str(instance.activity.id), filename])


class Workgroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(default="")
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name


class Swatch(models.Model):
    name = models.CharField(max_length=30)
    color_code = models.CharField(max_length=7)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Swatches"


class FocalPoint(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField(blank=True, null=True)
    lead = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(default="")
    start = models.DateField(auto_now_add=True)
    due = models.DateField(blank=True, null=True)
    gitlab_focal_point_id = models.IntegerField(blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True)
    is_complete = models.BooleanField(default=False)

    # Has due date for an instance of this object passed?
    def overdue_status(self):
        # Returns whether the Activity's due date has passed or not.
        if self.due and datetime.date.today() > self.due:
            return True

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Focal Points"

        # Prevents (at the database level) creation of two focal_points with the same slug in the same group
        unique_together = ("group", "slug")


class Activity(models.Model):
    title = models.CharField(max_length=140)
    focal_point = models.ForeignKey(FocalPoint, on_delete=models.CASCADE, null=True)
    created_date = models.DateField(auto_now_add=True, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    tags = TaggableManager(blank=True)
    color = models.ForeignKey(Swatch, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="activity_created_by",
        on_delete=models.CASCADE,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="activity_assigned_to",
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True, null=True)
    priority = models.PositiveIntegerField(blank=True, null=True)

    # Has due date for an instance of this object passed?
    def overdue_status(self):
        # Returns whether the Activity's due date has passed or not.
        if self.due_date and datetime.date.today() > self.due_date:
            return True

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("focalpoint:activity_detail", kwargs={"activity_id": self.id})

    # Auto-set the Activity creation / completed date
    def save(self, **kwargs):
        # If Activity is being marked complete, set the completed_date
        if self.completed:
            self.completed_date = datetime.datetime.now()
        super(Activity, self).save()

    class Meta:
        ordering = ["priority", "created_date"]


class Comment(models.Model):
    """
    Not using Django's built-in comments because we want to be able to save
    a comment and change activity details at the same time. Rolling our own since it's easy.
    """

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    email_from = models.CharField(max_length=320, blank=True, null=True)
    email_message_id = models.CharField(max_length=255, blank=True, null=True)

    body = models.TextField(blank=True)

    class Meta:
        # an email should only appear once per activity
        unique_together = ("activity", "email_message_id")

    @property
    def author_text(self):
        if self.author is not None:
            return str(self.author)

        assert self.email_message_id is not None
        return str(self.email_from)

    @property
    def snippet(self):
        body_snippet = textwrap.shorten(self.body, width=35, placeholder="...")
        # Define here rather than in __str__ so we can use it in the admin list_display
        return "{author} - {snippet}...".format(author=self.author_text, snippet=body_snippet)

    def __str__(self):
        return self.snippet


class Attachment(models.Model):
    """
    Defines a generic file attachment for use in M2M relation with Activity.
    """

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=datetime.datetime.now)
    file = models.FileField(upload_to=get_attachment_upload_dir, max_length=255)

    def filename(self):
        return os.path.basename(self.file.name)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def __str__(self):
        return f"{self.activity.id} - {self.file.name}"


class Board(models.Model):
    """
    Defines Kanban boards
    """
    name = models.CharField(max_length=25)
    slug = models.SlugField(default="")
    focal_point = models.ForeignKey(FocalPoint, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tags = TaggableManager(blank=True)

    def __str__(self):
        board_name = self.focal_point.name + ":" + self.name
        return board_name


class BoardColumn(models.Model):
    """
    Defines cards in focal_point board
    """
    title = models.CharField(max_length=30)
    slug = models.SlugField(default="")
    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    priority = models.PositiveIntegerField(blank=True, null=True)
    activity = models.ManyToManyField(Activity, blank=True)

    def __str__(self):
        card_title = self.board.name + ":" + self.title
        return card_title

    class Meta:
        ordering = ["priority"]


class BoardTemplate(models.Model):
    """
    Define default Kanban Board templates
    """
    name = models.CharField(max_length=50)
    slug = models.SlugField(default="", unique=True)
    columns = models.TextField(default="")
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["pk"]
