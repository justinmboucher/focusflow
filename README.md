# Welcome to FocusFlow!
Team Focus Management App

FocusFlow allows a manager to create and prioritize activities for their staff. 
Whether the activitity is associated to development, operations, or even personal activities, FocusFlow will track all
activities and provide the manager a holistic view of project completion.

## Environment setup
Getting the application installed is easy as installing the required packages via pip, and performing the database migrations. 
This may be done using a virtual environment for testing, or directly on the server using Postgres databases.
```
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## Integrations and Features
Current Integrations and Features include:

* Email Notification
* Productivity Reports
* activitity Commenting and Attachments
* Github/Gitlab Projects and Issues Linking
  * As Issues in Gitlab Projects are completed, the associated FocusFlow activitity will be completed as well.
* Event Audit Logging
* File Management
  
## Future Integrations

* Smart Card (CAC) Authentication via LDAP and Apache Proxy
* Clockify - Time management tracking
* Slack - Team collaboration

#### Please report issues if you find them!

## Known issues/weirdness
1. 3rd party issue in django-automated-logging. Workaround is to change:

    ```python
    # ~python3.7/site-packages/automated_logging/admin.py Line: 17
    
    def get_actions(self, request):
        actions = super(ReadOnlyAdminMixin, self).get_actions(request)
        del actions["delete_selected"]
        return actions
    ```
    
    to the following:
    
    ```python
    # ~python3.7/site-packages/automated_logging/admin.py Line: 17
    def get_actions(self, request):
        actions = super(ReadOnlyAdminMixin, self).get_actions(request)
        actions.pop('delete_selected', None)
        return actions
    ```