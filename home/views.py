# home/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test
from .models import Recipe


# ---------- Helper ----------
def _username_from_input(inp: str) -> str:
    """
    รับค่าที่ผู้ใช้กรอกมา (อาจเป็นอีเมลหรือยูสเซอร์เนม)
    ถ้าเป็นอีเมลจะแมปรายการเป็น username ก่อน authenticate
    """
    inp = (inp or "").strip()
    if "@" in inp:
        User = get_user_model()
        try:
            return User.objects.get(email__iexact=inp).username
        except User.DoesNotExist:
            return inp  # เผื่อกรณีตั้ง username = อีเมล
    return inp


def admin_required(view_func):
    """ต้องเป็นผู้ใช้ที่ล็อกอินแล้ว และเป็น staff หรือ superuser"""
    check = lambda u: u.is_authenticated and (u.is_staff or u.is_superuser)
    return user_passes_test(check, login_url="admin_login")(view_func)


# ---------- Public pages ----------
def home(request):
    return render(request, "home/home.html")


def register(request):
    User = get_user_model()

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password1 = request.POST.get("password1") or ""
        password2 = request.POST.get("password2") or ""

        if password1 != password2:
            messages.error(request, "รหัสผ่านไม่ตรงกัน")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "ชื่อผู้ใช้นี้มีอยู่แล้ว")
        elif email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, "อีเมลนี้มีอยู่แล้ว")
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            messages.success(request, "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ")
            return redirect("login")

    return render(request, "home/register.html")


def login_view(request):
    """
    ล็อกอินผู้ใช้ทั่วไป: ยอมรับทั้ง 'อีเมล' หรือ 'username'
    """
    if request.method == "POST":
        uname_input = request.POST.get("username")
        password = request.POST.get("password")
        username = _username_from_input(uname_input)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next") or "home"
            return redirect(next_url)
        messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    return render(request, "home/login.html")


# ---------- Admin dashboard (custom) ----------
def admin_login(request):
    """
    ล็อกอินแดชบอร์ดของระบบเอง (ไม่ใช่ Django admin)
    ยอมรับทั้งอีเมล/username และบังคับสิทธิ์ staff/superuser
    """
    if request.method == "POST":
        uname_input = request.POST.get("username")
        password = request.POST.get("password")
        username = _username_from_input(uname_input)

        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next") or "admin_recipes"
            return redirect(next_url)

        messages.error(request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง หรือไม่มีสิทธิ์เป็นแอดมิน")

    return render(request, "home/admin_login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


@admin_required
def admin_recipes(request):
    recipes = Recipe.objects.all()
    return render(request, "home/admin_recipes.html", {"recipes": recipes})


@admin_required
def add_recipe(request):
    if request.method == "POST":
        name = request.POST.get("name")
        category = request.POST.get("category")
        ingredients = request.POST.get("ingredients")
        instructions = request.POST.get("instructions")
        image = request.FILES.get("image")

        recipe = Recipe(name=name, category=category, ingredients=ingredients, instructions=instructions)
        if image:
            recipe.image = image
        recipe.save()
        messages.success(request, "บันทึกเมนูแล้ว")
        return redirect("admin_recipes")

    return render(request, "home/recipe_form.html", {"title": "เพิ่มเมนูอาหาร", "recipe": {}})


@admin_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)

    if request.method == "POST":
        recipe.name = request.POST.get("name")
        recipe.category = request.POST.get("category")
        recipe.ingredients = request.POST.get("ingredients")
        recipe.instructions = request.POST.get("instructions")
        image = request.FILES.get("image")
        if image:
            recipe.image = image
        recipe.save()
        messages.success(request, "แก้ไขเมนูแล้ว")
        return redirect("admin_recipes")

    return render(request, "home/recipe_form.html", {"title": "แก้ไขเมนูอาหาร", "recipe": recipe})


@admin_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    recipe.delete()
    messages.success(request, "ลบเมนูแล้ว")
    return redirect("admin_recipes")