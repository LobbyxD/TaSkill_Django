import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TaSkill.settings')
django.setup()

from django.contrib.auth.models import (User)
from accounts.models import (UserProfile)
from taskill_tasks.models import (Board, Board_Permission, Organization, Organization_Permission, Task_status, Task_status_link)

def get_bool(prompt: str):
    while True:
        try:
           return {"y":True,"n":False,"yes":True,"no":False,'true':True,'false':False,'t':True,'f':False}[input(prompt).lower()]
        except KeyError:
           print("Invalid input please enter y or n!")

def populate_database():
    print("Recommended: Y to all.")
    if get_bool("Populate task statuses + links?\n Y/N \n"):
        open_status = Task_status.objects.get_or_create(name='Open')[0]
        progress = Task_status.objects.get_or_create(name='In-Progress')[0]
        hold = Task_status.objects.get_or_create(name='On Hold')[0]
        review = Task_status.objects.get_or_create(name='Review')[0]
        completed = Task_status.objects.get_or_create(name='Completed')[0]
        
        open_link = Task_status_link.objects.get_or_create(current_status = open_status)[0]
        if not progress in open_link.next_statuses.all():
            open_link.next_statuses.add(progress)
            print('In-Progress was added to Open status')

        progress_link = Task_status_link.objects.get_or_create(current_status = progress)[0]
        if not open_status in progress_link.next_statuses.all():
            progress_link.next_statuses.add(open_status)
            print('Open was added to In-Progress status')
        if not hold in progress_link.next_statuses.all():
            progress_link.next_statuses.add(hold)
            print('Hold was added to In-Progress status')
        if not review in progress_link.next_statuses.all():
            progress_link.next_statuses.add(review)
            print('Review was added to In-Progress status')

        hold_link = Task_status_link.objects.get_or_create(current_status = hold)[0]
        if not progress in hold_link.next_statuses.all():
            hold_link.next_statuses.add(progress)
            print('In-Progress was added to Hold status')

        review_link = Task_status_link.objects.get_or_create(current_status = review)[0]
        if not progress in review_link.next_statuses.all():
            review_link.next_statuses.add(progress)
            print('In-Progress was added to Review status')
        if not completed in review_link.next_statuses.all():
            review_link.next_statuses.add(completed)
            print('Completed was added to Review status')

        completed_link = Task_status_link.objects.get_or_create(current_status = completed)[0]
        if not progress in completed_link.next_statuses.all():
            completed_link.next_statuses.add(progress)
            print('In-Progress was added to Completed status')
        print(open_status.next_statuses.all())
        print(progress.next_statuses.all())
        print(hold.next_statuses.all())
        print(review.next_statuses.all())
        print(completed.next_statuses.all())

        print("Tasks + links completed.\n")

    if get_bool("Populate users?\n Y/N \n"):
        created = 0
        # Organization
        try:
            organization_owner = User.objects.get(username = 'organization_owner')
            boards_view = User.objects.get(username = 'boards_view')
            boards_edit = User.objects.get(username = 'boards_edit')
        except:
            organization_owner = User.objects.create_user(username='organization_owner', email='organization_owner@g.com', password='postgrse')
            boards_view = User.objects.create_user(username='boards_view', email='boards_view@g.com', password='postgrse')
            boards_edit = User.objects.create_user(username='boards_edit', email='boards_edit@g.com', password='postgrse')
            created += 3
        # - Profile Creation
        organization_owner.profile.first_name = "organization_owner"
        organization_owner.profile.last_name = "Organization"
        organization_owner.profile.country = "IL"
        organization_owner.profile.save()

        boards_view.profile.first_name = "boards_view"
        boards_view.profile.last_name = "Organization"
        boards_view.profile.country = "IL"
        boards_view.profile.save()

        boards_edit.profile.first_name = "boards_edit"
        boards_edit.profile.last_name = "Organization"
        boards_edit.profile.country = "IL"
        boards_edit.profile.save()
        # Board
        try:
            board_owner = User.objects.get(username='board_owner')
            board_view = User.objects.get(username='board_view')
            change_status = User.objects.get(username='change_status')
            tasks_edit = User.objects.get(username='tasks_edit')
        except:
            board_owner = User.objects.create_user(username='board_owner', email='board_owner@g.com', password='postgrse')
            board_view = User.objects.create_user(username='board_view', email='board_view@g.com', password='postgrse')
            change_status = User.objects.create_user(username='change_status', email='change_status@g.com', password='postgrse')
            tasks_edit = User.objects.create_user(username='tasks_edit', email='tasks_edit@g.com', password='postgrse')
            created += 4
        # - Profile Creation
        board_owner.profile.first_name = "board_owner"
        board_owner.profile.last_name = "Board"
        board_owner.profile.country = "IL"
        board_owner.profile.save()

        board_view.profile.first_name = "board_view"
        board_view.profile.last_name = "Board"
        board_view.profile.country = "IL"
        board_view.profile.save()

        change_status.profile.first_name = "change_status"
        change_status.profile.last_name = "Board"
        change_status.profile.country = "IL"
        change_status.profile.save()

        tasks_edit.profile.first_name = "tasks_edit"
        tasks_edit.profile.last_name = "Board"
        tasks_edit.profile.country = "IL"
        tasks_edit.profile.save()

        try:
            pol = User.objects.get(username='pol')
        except:
            pol = User.objects.create_user(username='pol', email='pol@g.com', password='postgrse')
            created += 1
        pol.profile.first_name = "Pol"
        pol.profile.last_name = "Poli"
        pol.profile.country = "IL"
        pol.profile.save()


        print(f"User Populated, total created ({created})\n")

        if get_bool("Create and link users to pol's organ?\nY/N\n"):
            organ = Organization.objects.get_or_create(name="Populated", owner=pol)[0]
            pol.profile.organization = organ
            pol.profile.save()
            Organization_Permission.objects.get_or_create(organization = organ, user=pol, permissions='owner')[0]
            #Organ
            organization_owner.profile.organization = organ
            organization_owner.profile.save()
            Organization_Permission.objects.get_or_create(organization = organ, user=organization_owner, permissions='owner')

            boards_view.profile.organization = organ
            boards_view.profile.save()
            Organization_Permission.objects.get_or_create(organization = organ, user=boards_view, permissions='boards_view')

            boards_edit.profile.organization = organ
            boards_edit.profile.save()
            Organization_Permission.objects.get_or_create(organization = organ, user=boards_edit, permissions='boards_edit')
            Organization_Permission.objects.get_or_create(organization = organ, user=boards_edit, permissions='boards_view')

            #Board
            open_status = Task_status_link.objects.get(current_status__name='Open')
            populated_board = Board.objects.get_or_create(name='Populated Board', organization = organ, initial_task_status = open_status)[0]
            Board_Permission.objects.get_or_create(board = populated_board, user = pol, permissions = 'owner')

            board_owner.profile.organization = organ
            board_owner.profile.save()
            Board_Permission.objects.get_or_create(board = populated_board, user = board_owner, permissions = 'owner')

            board_view.profile.organization = organ
            board_view.profile.save()
            Board_Permission.objects.get_or_create(board = populated_board, user = board_view, permissions = 'board_view')

            change_status.profile.organization = organ
            change_status.profile.save()
            Board_Permission.objects.get_or_create(board = populated_board, user = change_status, permissions = 'change_status')

            tasks_edit.profile.organization = organ
            tasks_edit.profile.save()
            Board_Permission.objects.get_or_create(board = populated_board, user = tasks_edit, permissions = 'tasks_edit')
            Board_Permission.objects.get_or_create(board = populated_board, user = tasks_edit, permissions = 'board_view')
            print("Organization + Boards creation and links Completed\n")
                       
    
populate_database()