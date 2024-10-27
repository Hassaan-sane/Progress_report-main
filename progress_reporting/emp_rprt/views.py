from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from .forms import UsernameLoginForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db.models import Q
import openpyxl

# Create your views here.
from .models import EmpUser
from .models import Progress
from .models import WorkDetail
from .models import UserDepartment, Department, ProgressUpdated, WorkflowStage, Products

WORKFLOW_STAGES = [
    'Data Entry',
    'Uploading',
    'Photography',
    'Editing',
    'Reels',
    'Marketing'
]
# Creating workflow stages
# stage1 = WorkflowStage.objects.create(title='Data Entry', order=1)
# stage4 = WorkflowStage.objects.create(title='Uploading', order=4)
# stage2 = WorkflowStage.objects.create(title='Photography', order=2)
# stage3 = WorkflowStage.objects.create(title='Editing', order=3)
# stage5 = WorkflowStage.objects.create(title='Reels', order=5)
# stage6 = WorkflowStage.objects.create(title='Marketing', order=6)

# # Defining next stages
# stage1.next_stages.add(stage2)  # Data Entry goes to Photgraphy
# stage2.next_stages.add(stage3)  # Photgraphy goes to Editing
# stage3.next_stages.add(stage4, stage5, stage6)

def product_progress_view(request):
    user = request.user  # Get the current logged-in user

    products = Products.objects.all()
    progress_data = {}
    # Get the work details the user is allowed to see based on UserDepartment
    allowed_work = UserDepartment.objects.filter(user=user)
    
    for product in products:
        work_progress_list = []
        for aw in allowed_work:
            # print(aw.user)
            # print(aw.department)
            # print(aw.work)
            # Fetch progress entries for the allowed work
            progress_entries = Progress.objects.filter(workflow_stage__title=aw.work, product = product).first()
            work_progress_list.append(progress_entries if progress_entries else None)
            
            # for progress in progress_entries:
            #     if product_id not in progress_data:
            #         progress_data[product.id] = []  # Initialize list if not present
                
                # progress_data[product_id].append(progress)  # Append the progress entry to the list

        progress_data[product.sku] = work_progress_list
    
    for product_id, work_progress_list in progress_data.items():
        print(f"Product ID: {product_id}")
    
        for progress in enumerate(work_progress_list, start=1):
            if progress:
                print(f"Progress Object - {progress}")
            else:
                print(f"No progress data available")

    # Now, progress_data is a dictionary where each key is a product ID and each value is a list of Progress objects
    return render(request, 'emp_rprt/progress_report.html', {
        'progress_data': progress_data,
        'allowed_work':allowed_work
        })

@csrf_exempt
def save_progress_view(request):
    user = request.user
    if request.method == 'POST':
        data = json.loads(request.body)
        progress = data.get('progress')
        product_id = data.get('product_id')
        work_id = data.get('work_id')
        user_id = data.get('user_id')
        new_status = data.get('status')
        
        try:
            progress = Progress.objects.get(id=progress, 
                        product__id=product_id, 
                        workflow_stage__id=work_id)
                    
            if new_status == "not_started":     

                progress.status = "not_started"
                progress.user = user
                # progress.workflow_stage = progress.workflow_stage.next_stages.first()
                progress.save()
                
                ProgressUpdated.objects.create(
                    product=progress.product,
                    user=user,
                    workflow_stage=progress.workflow_stage,
                    status_changed_to=new_status,
                )
                return JsonResponse({'success': True})
            
            elif new_status == "ongoing":

                progress.status = "ongoing"
                progress.user = user
                # progress.workflow_stage = progress.workflow_stage.next_stages.first()
                progress.save()
                
                ProgressUpdated.objects.create(
                    product=progress.product,
                    user=user,
                    workflow_stage=progress.workflow_stage,
                    status_changed_to=new_status,
                )
                return JsonResponse({'success': True})
            
            elif new_status == "completed":

                progress.status = "completed"
                progress.user = user
                # progress.workflow_stage = progress.workflow_stage.next_stages.first()
                progress.save()
                
                print(progress.workflow_stage.next_stages.first())
                
                ProgressUpdated.objects.create(
                    product=progress.product,
                    user=user,
                    workflow_stage=progress.workflow_stage,
                    status_changed_to=new_status,
                )
                
                if progress.workflow_stage.next_stages.first():
                    Progress.objects.create(product = progress.product,
                                            workflow_stage = progress.workflow_stage.next_stages.first(),
                                            status = "not_started")
                    
                    ProgressUpdated.objects.create(
                        product=progress.product,
                        user=user,
                        workflow_stage=progress.workflow_stage.next_stages.first(),
                        status_changed_to="not_started",
                    )
                return JsonResponse({'success': True})
        except Progress.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Progress not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# def save_progress(request):
#     if request.method == 'POST':
#         for key, value in request.POST.items():
#             if key.startswith('progress_'):
#                 progress_id = key.split('_')[1]  # Get the progress ID
#                 new_status = value  # Get the new status from dropdown

#                 # Update the existing progress entry
#                 progress = Progress.objects.get(id=progress_id)
#                 progress.status = new_status
#                 progress.save()

#                 # Check if the new status is 'completed'
#                 if new_status == 'completed':
#                     # Get the next stages for the current workflow stage
#                     next_stages = progress.workflow_stage.next_stages.all()
#                     for next_stage in next_stages:
#                         Progress.objects.create(
#                             work=progress.work,
#                             product=progress.product,
#                             user=progress.user,  # Optionally carry over user
#                             department=progress.department,
#                             workflow_stage=next_stage,
#                             status='not_started',  # Set new tasks as 'not_started'
#                         )

#                 # Optionally log this update in the ProgressUpdated model
#                 ProgressUpdated.objects.create(
#                     product=progress.product,
#                     user=request.user,
#                     work=progress.work,
#                     workflow_stage=progress.workflow_stage,
#                     status_changed_to=new_status,
#                 )

#         return JsonResponse({'status': 'success'})

#     return JsonResponse({'status': 'failed'}, status=400)

def progress_table_view(request):
    user = request.user
    user_departments = UserDepartment.objects.filter(user=user).select_related('work')

    # Prepare a set of Department titles for quick lookup
    user_work_titles = set(user_departments.values_list('work__title', flat=True))

    # Fetch progress data for the current user
    progress_data = Progress.objects.filter(user=user).select_related('product', 'workflow_stage')
    positions = Department.objects.all()

    return render(request, 'emp_rprt/progress_table.html', {
        'progress_data': progress_data,
        'user_departments': user_departments,
        'user_work_titles': user_work_titles,  # Pass the titles to the template
        'positions': positions,
        'csrf_token': request.META.get('CSRF_COOKIE'),  # Pass CSRF token for the JavaScript
    })


# def progress_table_view(request):
#     user = request.user
#     user_departments = UserDepartment.objects.filter(user=user).select_related('work')
    
#     # Prepare a set of Depatment titles for quick lookup
#     user_work_titles = set(user_departments.values_list('work__title', flat=True))
#     print(user_work_titles)

#     progress_data = Progress.objects.filter(user=user)
#     positions = Department.objects.all()
#     workList = WorkDetail.objects.all()  # Assuming you have a Work model

#     return render(request, 'emp_rprt/progress_table.html', {
#         'progress_data': progress_data,
#         'user_departments': user_departments,
#         'user_work_titles': user_work_titles,  # Pass the titles to the template
#         'positions': positions,
#         'workList': workList,
#     })


def login_signup_view(request):
    return render(request, 'emp_rprt/login_signup.html')

def signup_view(request):
    # Fetch positions and works from the database to show in the dropdowns
    departments = Department.objects.all()
    works = WorkDetail.objects.all()

    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        position_id = request.POST['position_id']  # ID of selected Depatment
        work_id = request.POST['work_id']  # ID of selected work

        # Check if the email is already in use
        if EmpUser.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use.')
        else:
            # Create a new user
            user = EmpUser.objects.create_user(username=username, email=email, password=password)
            user.name = name
            user.save()

            # Get selected Depatment and work
            department = Department.objects.get(id=position_id)
            work = WorkDetail.objects.get(id=work_id)

            # Create an entry in the UserDepatment table
            user_position = UserDepartment.objects.create(user=user, department=department, work=work)
            user_position.save()

            messages.success(request, 'Account created successfully.')

            # Log in the user and redirect to progress page
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('progress')  # Change 'progress' to the correct URL name
    else:
        # If it's a GET request, display the signup form

        return render(request, 'emp_rprt/signup.html', {
            'positions': departments,
            'works': works
        })

def login_view(request):
    if request.method == 'POST':
        form = UsernameLoginForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['username']
            try:
                # Attempt to find a user with this username
                user = EmpUser.objects.get(name=name)

                # Log in the user without a password
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')

                # Redirect based on superuser status
                if user.is_superuser:
                    return redirect('dashboard')  # Redirect to dashboard for superusers
                else:
                    return redirect('product_progress')  # Redirect to progress page for regular users

            except EmpUser.DoesNotExist:
                # Add an error if the user does not exist
                form.add_error('username', 'No user with this username found')

    else:
        form = UsernameLoginForm()

    return render(request, 'emp_rprt/login.html', {'form': form})

def logout_view(request):
    logout(request)  # Log the user out
    return redirect('login') 

def dashboard(request):
    return render(request, 'emp_rprt/dashboard.html')

def data_entry(request):
    return render(request, 'emp_rprt/data_entry.html')

def upload_excel(request):
    print("imhere")
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['file']
            workbook = openpyxl.load_workbook(excel_file)
            worksheet = workbook.active

            # Extract data from the Excel file
            products = []
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                sku, title, quantity = row
                products.append({
                    'sku': sku,
                    'title': title,
                    'quantity': quantity
                })

            # Return data as JSON response
            return JsonResponse({'products': products})
    return JsonResponse({'error': 'Invalid request'}, status=400)


# def update_progress(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         progress_id = data.get('progress_id')
#         product_id = data.get('product_id')
#         work_id = data.get('work_id')
#         user_id = data.get('user_id')
#         new_status = data.get('status')

#         try:
#             # Update the specific Progress entry
#             progress = Progress.objects.get(id=progress_id, product_id=product_id, work_id=work_id, user_id=user_id)
#             progress.status = new_status
#             progress.save()

#             # Add a new entry to the ProgressUpdated table
#             ProgressUpdated.objects.create(
#                 product_id=product_id,
#                 user_id=user_id,
#                 work_id=work_id,
#                 status_changed_to=new_status,
#                 date_changed=datetime.now()  # Current time of change
#             )

#             # If the new status is 'completed', update the next work in the workflow
#             if new_status == 'completed':
#                 current_work_index = WORKFLOW_STAGES.index(progress.work.title)
#                 if current_work_index + 1 < len(WORKFLOW_STAGES):  # Check if there is a next work
#                     next_work_title = WORKFLOW_STAGES[current_work_index + 1]
                    
#                     # Check if the next work already exists in Progress
#                     next_progress = Progress.objects.filter(product_id=product_id, work__title=next_work_title, user_id=user_id).first()
#                     if next_progress:
#                         next_progress.status = 'not_started'
#                         next_progress.save()
#                     else:
#                         # Optionally, create a new Progress entry for the next work
#                                     # Update the specific Progress entry
#                         progress = Progress.objects.get(id=progress_id, product_id=product_id, work_id=work_id, user_id=user_id)
#                         progress.status = 'not_started'
#                         progress.work = WorkDetail.objects.get(title=next_work_title)
#                         progress.save()

#                         # Add a new entry to the ProgressUpdated table
#                         ProgressUpdated.objects.create(
#                             product_id=product_id,
#                             user_id=user_id,
#                             work_id=progress.work.id,
#                             status_changed_to="not_started",
#                             date_changed=datetime.now()  # Current time of change
#                         )
#                         # Progress.objects.create(
#                         #     product_id=product_id,
#                         #     user_id=user_id,
#                         #     work=WorkDetail.objects.get(title=next_work_title),  # Ensure you have the WorkDetail instance
#                         #     status='ongoing'
#                         # )

#             return JsonResponse({'success': True})
#         except Progress.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'Progress not found'}, status=404)
#         except Exception as e:
#             return JsonResponse({'success': False, 'error': str(e)}, status=500)

#     return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)