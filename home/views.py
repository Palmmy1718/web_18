# home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Recipe, Category
from django.contrib.auth.decorators import login_required

# ---------- ฟังก์ชันสำหรับสมาชิกแก้ไขสูตรอาหารของตัวเอง ----------
@login_required(login_url='login')
def user_edit_recipe(request, recipe_id):
    """ฟังก์ชันสำหรับสมาชิกแก้ไขสูตรอาหารของตัวเอง"""
    recipe = get_object_or_404(Recipe, pk=recipe_id, creator=request.user)
    if request.method == "POST":
        recipe.name = request.POST.get("name")
        category_id = request.POST.get("category")
        recipe.ingredients = request.POST.get("ingredients")
        recipe.instructions = request.POST.get("instructions")
        image = request.FILES.get("image")

        recipe.category = get_object_or_404(Category, id=category_id)
        if image:
            recipe.image = image
        recipe.save()
        messages.success(request, "แก้ไขสูตรอาหารของคุณเรียบร้อยแล้ว!")
        return redirect("user_recipes")

    categories = Category.objects.all()
    return render(request, "home/recipe_form.html", {"title": "แก้ไขสูตรของฉัน", "recipe": recipe, "categories": categories})

# ---------- ฟังก์ชันสำหรับสมาชิกลบสูตรอาหารของตัวเอง ----------
@login_required(login_url='login')
def user_delete_recipe(request, recipe_id):
    """ฟังก์ชันสำหรับสมาชิกลบสูตรอาหารของตัวเอง"""
    recipe = get_object_or_404(Recipe, pk=recipe_id, creator=request.user)
    recipe_name = recipe.name
    recipe.delete()
    messages.success(request, f'ลบสูตร "{recipe_name}" เรียบร้อยแล้ว!')
    return redirect("user_recipes")

# ---------- Helper Decorator ----------
def admin_required(view_func):
    """Decorator ที่เช็คว่าผู้ใช้เป็น Admin (staff) หรือไม่"""
    check = lambda u: u.is_authenticated and u.is_staff
    return user_passes_test(check, login_url="login")(view_func)

# ---------- หน้าเว็บสำหรับทุกคน ----------
def home(request):
    """หน้าแรก แสดงสูตรอาหารทั้งหมด"""
    categories = Category.objects.all()
    recipes = Recipe.objects.all()
    return render(request, "home/home.html", {"categories": categories, "recipes": recipes})

# ---------- ฟังก์ชันสำหรับสมาชิกดูสูตรอาหารของตัวเอง ----------
@login_required(login_url='login')
def user_recipes(request):
    recipes = Recipe.objects.filter(creator=request.user).order_by('-created_at')
    return render(request, "home/user_recipes.html", {"recipes": recipes})

# ---------- ฟังก์ชันดูรายละเอียดเมนูและนับยอดเข้าชม ----------
def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.view_count += 1
    recipe.save(update_fields=["view_count"])
    return render(request, "home/recipe_detail.html", {"recipe": recipe})



# ---------- ระบบสมาชิก (Auth) ----------
def register(request):
    """ฟังก์ชันสำหรับหน้าสมัครสมาชิก"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'รหัสผ่านที่ยืนยันไม่ตรงกัน!')
            return redirect('register')
        if User.objects.filter(username=username).exists():
            messages.error(request, f'ชื่อผู้ใช้ "{username}" ถูกใช้งานแล้ว!')
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, f'อีเมล "{email}" นี้ถูกใช้งานแล้ว!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ')
        return redirect('login')
    return render(request, "home/register.html")

def login_view(request):
    """ฟังก์ชันสำหรับหน้า Login (จัดการทั้ง Admin และ User)"""
    if request.method == 'POST':
        user_input = request.POST.get("username")
        passw = request.POST.get("password")
        
        username = user_input
        if "@" in user_input:
             try:
                username = User.objects.get(email__iexact=user_input).username
             except User.DoesNotExist:
                pass

        user = authenticate(request, username=username, password=passw)

        if user is not None:
            login(request, user)
            if user.is_staff: # is_staff เช็คว่าเป็น Admin หรือไม่
                return redirect('admin_recipes')
            else:
                return redirect('home')
        else:
            messages.error(request, 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง!')
            return redirect('login')
            
    return render(request, "home/login.html")

def logout_view(request):
    """ฟังก์ชันสำหรับ Logout"""
    logout(request)
    messages.success(request, 'ออกจากระบบเรียบร้อยแล้ว')
    return redirect('home')

# ---------- ฟังก์ชันสำหรับสมาชิกที่ Login แล้ว ----------
@login_required(login_url='login')
def user_add_recipe(request):
    """ฟังก์ชันสำหรับให้ User ทั่วไปเพิ่มสูตรอาหาร"""
    if request.method == "POST":
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        ingredients = request.POST.get("ingredients")
        instructions = request.POST.get("instructions")
        image = request.FILES.get("image")

        category = get_object_or_404(Category, id=category_id)

        recipe = Recipe(
            name=name,
            category=category,
            ingredients=ingredients,
            instructions=instructions,
            creator=request.user # กำหนดให้ตัวเองเป็นผู้สร้าง
        )
        if image:
            recipe.image = image
        recipe.save()
        messages.success(request, "เพิ่มสูตรอาหารของคุณเรียบร้อยแล้ว!")
        return redirect("home")

    # เตรียมข้อมูล Category สำหรับ Dropdown ในฟอร์ม
    categories = Category.objects.all()
    return render(request, "home/recipe_form.html", {"title": "เพิ่มสูตรอาหารใหม่", "categories": categories})


# ---------- ส่วนจัดการของ Admin ----------
@admin_required
def admin_recipes(request):
    """หน้าแสดงรายการอาหารทั้งหมดสำหรับ Admin"""
    all_recipes = Recipe.objects.all().order_by('-created_at')
    recipe_count = all_recipes.count()
    # Prepare category data for chart
    categories = Category.objects.all()
    category_labels = [cat.name for cat in categories]
    category_counts = [all_recipes.filter(category=cat).count() for cat in categories]
    context = {
        'recipes': all_recipes,
        'recipe_count': recipe_count,
        'category_labels': category_labels,
        'category_counts': category_counts,
    }
    return render(request, "home/admin_recipes.html", context)

@admin_required
def edit_recipe(request, recipe_id):
    """ฟังก์ชันสำหรับให้ Admin แก้ไขสูตรอาหารของทุกคน"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.method == "POST":
        recipe.name = request.POST.get("name")
        category_id = request.POST.get("category")
        recipe.ingredients = request.POST.get("ingredients")
        recipe.instructions = request.POST.get("instructions")
        image = request.FILES.get("image")

        recipe.category = get_object_or_404(Category, id=category_id)
        
        if image:
            recipe.image = image
        recipe.save()
        messages.success(request, "แก้ไขเมนูเรียบร้อยแล้ว")
        return redirect("admin_recipes")

    categories = Category.objects.all()
    return render(request, "home/recipe_form.html", {"title": "แก้ไขเมนูอาหาร", "recipe": recipe, "categories": categories})

@admin_required
def delete_recipe(request, recipe_id):
    """ฟังก์ชันสำหรับให้ Admin ลบสูตรอาหารของทุกคน"""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe_name = recipe.name
    recipe.delete()
    messages.success(request, f'ลบเมนู "{recipe_name}" เรียบร้อยแล้ว')
    return redirect("admin_recipes")

# หมายเหตุ: ฟังก์ชัน add_recipe ของ Admin จะใช้ร่วมกับของ User ได้เลย
# เราจึงสร้าง URL ให้ชี้ไปที่ user_add_recipe ได้
# แต่ถ้าต้องการ Logic แยก ก็สามารถสร้างฟังก์ชันใหม่ได้
@admin_required
def add_recipe(request):
    """ฟอร์มเพิ่มสูตรอาหารสำหรับ Admin (ใช้ฟอร์มเดียวกับ User)"""
    return user_add_recipe(request)