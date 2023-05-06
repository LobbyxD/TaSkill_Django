from django import forms
from django.contrib.auth.models import User
from django.db.models import Q

from .models import (Board, Board_Permission, Organization,
                     Organization_Permission, Task, Task_status_link)


##########################################
############## Organization ##############
##########################################
class Organization_Creation(forms.ModelForm):
    class Meta:
        model= Organization
        fields = ['name']
    
    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super(Organization_Creation, self).__init__(*args, **kwargs)
        if self.user.is_staff:
            self.fields['owner'] = forms.ModelChoiceField(
                queryset=User.objects.all(),
                widget=forms.Select(attrs={
                    'class' : "form-select text-center",
                        }))
        else:
            self.user = self.user  

class Give_Organization_Permission(forms.ModelForm):
    class Meta:
        model = Organization_Permission
        fields = '__all__'
        widgets = {
            'permissions': forms.Select(attrs={
                'class' : "form-select text-center",
                }),
        }
        labels = {
            'permissions':'Permission',
        }

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        self.organization = kwargs.pop('organization', None)
        super(Give_Organization_Permission, self).__init__(*args, **kwargs)
        organ = Organization.objects.filter(id=self.organization.id)
        self.fields['organization'] = forms.ModelChoiceField(
                queryset=organ,
                initial=organ.first(),
                to_field_name='name',
                widget=forms.TextInput(attrs={
                'readonly': 'readonly',
                'class' : "form-control text-center",
                    })
                  )
        if self.user.is_staff:
            users = User.objects.filter(profile__organization = organ.first())
            self.fields['user'] = forms.ModelChoiceField(
                queryset=users,
                empty_label='Select User',
                widget=forms.Select(attrs={
                    'class' : "form-select text-center",
                        })
                )
        else:
            users = User.objects.filter(
                profile__organization = organ.first()
                ).exclude(
                    Q(id=self.user.id) | Q(id=organ.first().owner.id)
                    )

            self.fields['user'] = forms.ModelChoiceField(
                queryset=users,
                empty_label='Select User',
                widget=forms.Select(attrs={
                    'class' : "form-select text-center",
                        })
                )    

###################################
############## Board ##############
###################################

class Board_Creation(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['organization', 'name', 'initial_task_status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class' : "form-control text-center",
                'placeholder': 'Enter Name',
                'aria-label': "Name"
                    })
        }
        
    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        super(Board_Creation, self).__init__(*args, **kwargs)
        task_status=Task_status_link.objects.all()
        if self.user.is_staff:
            self.fields['organization'] = forms.ModelChoiceField(
                queryset=Organization.objects.all(),
                empty_label='Choose Organization',
                widget=forms.Select(attrs={
                    'class' : "form-select text-center",
                        }))
            self.fields['initial_task_status'] = forms.ModelChoiceField(
                queryset=task_status,
                empty_label='Select Inital Status',
                to_field_name='current_status',
                widget = forms.Select(attrs={
                    'class' : "form-select text-center",
                        }))
        else:
            organ = Organization.objects.filter(profiles__id = self.user.profile.id)
            self.fields['organization'] = forms.ModelChoiceField(queryset=organ, initial=organ.first(),
                to_field_name='name' ,
                widget=forms.TextInput(attrs={
                    'readonly':'readonly',
                    'class' : "form-control text-center",
                        }))

            self.fields['initial_task_status'] = forms.ModelChoiceField(
                queryset=task_status,
                initial=task_status.first(),
                to_field_name='current_status',
                widget=forms.TextInput(attrs={
                    'readonly':'readonly',
                    'class' : "form-control text-center",
                        }))       

class Give_Board_Permission(forms.ModelForm):
    class Meta:
        model = Board_Permission
        fields = '__all__'
        widgets = {
            'permissions': forms.Select(attrs={
                'style':'width:206.8px',
                'class' : "form-select text-center",
                }),
        }
        labels = {
            'permissions':'Permission',
        }

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        self.board_id = kwargs.pop('board', None).id
        super(Give_Board_Permission, self).__init__(*args, **kwargs)
        board =  Board.objects.filter(id = self.board_id)
        self.fields['board'] = forms.ModelChoiceField(
            queryset=board,
            initial=board.first(),
            to_field_name='name',
            widget=forms.TextInput(attrs={
                'readonly':'readonly',
                'class' : "form-control text-center",
                    })
                )
        users = User.objects.filter(
            profile__organization__id = board.first().organization_id
            ).exclude(
                Q(id=self.user.id) | Q(id=board.first().organization.owner.id)
                )
        self.fields['user'] = forms.ModelChoiceField(queryset=users, empty_label='Select User', widget=forms.Select(attrs={
            'style':'width:206.8px',
            'class' : "form-select text-center",
            }))

##################################
############## Task ##############
##################################

class Task_Creation(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
        exclude = ['slug', 'assignee_progress']
        widgets = {
            'title': forms.TextInput(attrs={
                'style':'width:400px',
                'class' : "form-control text-center",
                "placeholder":"Enter Title"
                }),
            'description': forms.Textarea(attrs={
                'style':'width:400px',
                'class' : "form-control text-center",
                'placeholder': 'Enter Description'
                })
        }

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        self.board_id = kwargs.pop('board', None).id
        super(Task_Creation, self).__init__(*args, **kwargs)
        board =  Board.objects.filter(id = self.board_id)
        self.fields['board'] = forms.ModelChoiceField(
                queryset=board,
                initial=board.first(),
                to_field_name='name',
                widget=forms.TextInput(attrs={
                'readonly':'readonly',
                'style':'width:400px',
                'class' : "form-control text-center",
                })
                  )

        task_statuses = Task_status_link.objects.all()
        self.fields['status'] = forms.ModelChoiceField(
            queryset=task_statuses,
            initial=board.first().initial_task_status,
            to_field_name='current_status',
            widget=forms.TextInput(attrs={
                'readonly':'readonly',
                'style':'width:400px',
                'class' : "form-control text-center",
                })
                )

        users = User.objects.filter(
            profile__organization__id = board.first().organization_id
                ).exclude(
                    Q(id=self.user.id) | Q(id=board.first().organization.owner.id)
                    )

        self.fields['assignee'] = forms.ModelMultipleChoiceField(queryset=users, widget=forms.SelectMultiple(attrs={
            'style':'width:400px; height:200px;',
            'class' : "form-select text-center",
            }))
        

class Task_edit_users(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['assignee']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user', None)
        self.board_id = kwargs.pop('board', None).id
        super(Task_edit_users, self).__init__(*args, **kwargs)
        board =  Board.objects.filter(id = self.board_id)
        users = User.objects.filter(
            profile__organization__id = board.first().organization_id).exclude(
                Q(id=self.user.id) |
                Q(id=board.first().organization.owner.id)
                )
        self.fields['assignee'] = forms.ModelMultipleChoiceField(queryset=users, initial=users.first(), widget=forms.SelectMultiple(attrs={
            'style':'width:206.8px; height:200px;',
            'class' : "form-select text-center",
            }))

class Task_make_progress(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['assignee_progress']
        widgets = {
            'assignee_progress': forms.Textarea(attrs={
                'style':'width:400px',
                'class' : "form-control text-center",
                'placeholder': 'Enter Description'
                })
            }

class Task_change_status(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['status']

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop('user')
        super(Task_change_status, self).__init__(*args, **kwargs)
        statuses = Task_status_link.objects.all()
        self.fields['status'] = forms.ModelChoiceField(queryset=statuses, widget=forms.Select(attrs={
            'style':'width:206.8px;',
            'class' : "form-select text-center",
            }))
        self.fields['status'].empty_label = None
        self.fields['status'].label = 'Current status:'
        