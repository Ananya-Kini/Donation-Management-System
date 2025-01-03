from django.shortcuts import render, redirect
from django.db import connection,OperationalError,transaction,IntegrityError
from django.contrib import messages
import random

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def home(request):
    return render(request, 'home.html')

def donor_register(request):
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            password=request.POST.get('password')
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO Donor (name, email, phone_number, address,password)
                    VALUES (%s, %s, %s, %s,%s)
                """, [name, email, phone, address,password])
            messages.success(request, 'Registration successful! Please login.')
            return redirect('app:donor_login')          
        except Exception as e:
            messages.error(request, 'An unexpected error occurred. Please try again.')
    return render(request, 'donor_register.html')

def donor_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Donor WHERE email = %s", [email])
            donor = dictfetchall(cursor)
            if donor and donor[0]['password'] == password:
                request.session['donor_id'] = donor[0]['donor_id']
                return redirect('app:donor_dashboard')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')  
    return render(request, 'donor_login.html')

def donor_dashboard(request):
    if 'donor_id' not in request.session:
        return redirect('app:donor_login')
    donor_id = request.session['donor_id']
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(s.sponsorship_id) as active_sponsorships
            FROM Sponsorship s
            JOIN Child c ON s.child_id = c.child_id
            WHERE s.donor_id = %s AND s.status = 'Active'
        """, [donor_id])
        active_count = cursor.fetchone()[0]
        cursor.execute("""
            SELECT s.*, c.name as child_name 
            FROM Sponsorship s 
            JOIN Child c ON s.child_id = c.child_id 
            WHERE s.donor_id = %s
        """, [donor_id])
        sponsorships = dictfetchall(cursor)
        cursor.execute("SELECT * FROM Child WHERE child_id NOT IN (SELECT child_id FROM Sponsorship WHERE status = 'Active')")
        available_children = dictfetchall(cursor)
    return render(request, 'donor_dashboard.html', {
        'sponsorships': sponsorships,                  
        'available_children': available_children,       
        'active_count': active_count,                 
    })


def fieldworker_register(request):
    if request.method == 'POST':
        try:
            national_id = request.POST.get('national_id')  
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone_number = request.POST.get('phone') 
            region = request.POST.get('region')
            password=request.POST.get('password')
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO FieldWorker (field_worker_id, name, email, phone_number, region,password)
                    VALUES (%s, %s, %s, %s, %s,%s)
                """, [national_id, name, email, phone_number, region,password])
            messages.success(request, 'Registration successful! Please login.')
            return redirect('app:fieldworker_login')
        except Exception as e:
            messages.error(request, e)   
    return render(request, 'fieldworker_register.html')

def fieldworker_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM FieldWorker WHERE email = %s", [email])
            worker = dictfetchall(cursor)  
            if worker and worker[0]['password'] == password:
                request.session['worker_id'] = worker[0]['field_worker_id']
                return redirect('app:fieldworker_dashboard')
            else:
                messages.error(request, 'Invalid email or password. Please try again.')
    return render(request, 'fieldworker_login.html')

def fieldworker_dashboard(request):
    if 'worker_id' not in request.session:
        return redirect('fieldworker_login')
    worker_id = request.session['worker_id']
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Inventory WHERE field_worker_id = %s", [worker_id])
        inventory = dictfetchall(cursor)
        cursor.execute("SELECT * FROM Child WHERE field_worker_id = %s", [worker_id])
        children = dictfetchall(cursor)
        cursor.execute("SELECT CountChildrenForFieldWorker(%s) AS total_children", [worker_id])
        total_children = cursor.fetchone()[0]
    return render(request, 'fieldworker_dashboard.html', {
        'inventory': inventory,
        'children': children,
        'total_children': total_children,  
    })

def add_inventory(request):
    if request.method == 'POST' and 'worker_id' in request.session:
        item_name = request.POST.get('item_name')
        quantity = request.POST.get('quantity')
        condition = request.POST.get('condition')
        worker_id = request.session['worker_id']
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Inventory (item_name, quantity, `condition`, field_worker_id)
                VALUES (%s, %s, %s, %s)
            """, [item_name, quantity, condition, worker_id])
        return redirect('app:fieldworker_dashboard')
    return redirect('app:fieldworker_login')

def create_sponsorship(request):
    if request.method == 'POST' and 'donor_id' in request.session:
        donor_id = request.session['donor_id']
        child_id = request.POST.get('child_id')
        start_date = request.POST.get('start_date')
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO Sponsorship (donor_id, child_id, start_date, status)
                VALUES (%s, %s, %s, 'Active')
            """, [donor_id, child_id, start_date])
        return redirect('app:donor_dashboard')
    return redirect('app:donor_login')

def donate_clothes(request):
    if request.method == 'POST':
        clothes_type = request.POST.get('clothes_type')
        quantity = request.POST.get('quantity')
        with connection.cursor() as cursor:
            cursor.execute("SELECT field_worker_id FROM FieldWorker")
            field_workers = cursor.fetchall()  
        if field_workers:
            random_worker_id = random.choice(field_workers)[0]  
        else:
            messages.error(request, "No available field workers to assign.")
            return redirect('app:donor_dashboard')
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO Inventory (item_name, quantity, `condition`, field_worker_id) VALUES (%s, %s, %s, %s)",
                [clothes_type, quantity, 'new', random_worker_id]  
            )
        messages.success(request, "Clothes donation recorded successfully.")
        return redirect('app:donor_dashboard')


def create_child(request):
    if request.method == 'POST':
        child_name = request.POST.get('child_name', '').strip()
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '').strip()
        education_status = request.POST.get('education', 'Not Specified').strip()
        field_worker_id = request.POST.get('field_worker_id', '').strip()
        if not child_name or not age or not gender or not field_worker_id:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'fieldworker_dashboard.html', {'child_name': child_name, 'age': age, 'gender': gender, 'education_status': education_status, 'field_worker_id': field_worker_id})
        try:
            with transaction.atomic(), connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO Child (name, age, gender, education_status, field_worker_id)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [child_name, age, gender, education_status, field_worker_id]
                )
            messages.success(request, "Child created successfully.")
            messages.info(request, "A log entry has also been created for this child.")
            return redirect('app:fieldworker_dashboard')
        except OperationalError as e:
            print(f"OperationalError: {e}")           
            if "A child with this name already exists." in str(e):
                messages.info(request, "A child with this name already exists. Please check the name and try again.")
            else:
                messages.error(request, "An error occurred while creating the child record.")            
            return render(request, 'fieldworker_dashboard.html', {
                'child_name': child_name,
                'age': age,
                'gender': gender,
                'education_status': education_status,
                'field_worker_id': field_worker_id
            })
    return render(request, 'fieldworker_dashboard.html')


def delete_inventory_item(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT inventory_id, item_name FROM Inventory")
        inventory_items = cursor.fetchall() 
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM Inventory WHERE inventory_id = %s",
                [item_id]
            )
        messages.success(request, "Inventory item deleted successfully.")
        return redirect('app:fieldworker_dashboard')
    return render(request, 'fieldworker_dashboard.html', {'inventory_items': inventory_items})

def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        worker_id = request.session.get('worker_id')
        if worker_id:
            with connection.cursor() as cursor:
                cursor.execute("SELECT password FROM FieldWorker WHERE field_worker_id = %s", [worker_id])
                current_password = cursor.fetchone()[0]
                if current_password == old_password:
                    cursor.execute("UPDATE FieldWorker SET password = %s WHERE field_worker_id = %s", [new_password, worker_id])
                    messages.success(request, 'Password changed successfully.')
                    return redirect('app:fieldworker_dashboard')
                else:
                    messages.error(request, 'Old password is incorrect.')
        else:
            messages.error(request, 'Please log in to change your password.')

    return render(request, 'change_password.html')