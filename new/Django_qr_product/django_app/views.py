import qrcode
from io import BytesIO
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


def create_product(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        expiration_date = request.POST.get("expiration_date")
        picture = request.FILES.get("picture")

        product = Product.objects.create(
            name=name,
            description=description,
            expiration_date=expiration_date,
            picture=picture,
        )

        product_url = f"http://0.0.0.0:8000/product/{product.id}/"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(product_url)
        qr.make(fit=True)

        qr_code_img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        qr_code_img.save(buffer, format="PNG")

        qr_code_path = default_storage.save(
            f"qr_codes/{product.id}.png", ContentFile(buffer.getvalue())
        )

        product.qr_code.name = qr_code_path
        product.save()

        return redirect("product_detail", product_id=product.id)
    else:
        return render(request, "create_product.html")


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "product_detail.html", {"product": product})


def home(request):
    products = Product.objects.all()
    return render(request, "home.html", context={"products": products})


def logout_view(request):
    logout(request)
    return redirect("home")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

    return render(request, "login.html", context={})


def profile(request, username):
    return render(request, "profile.html", context={"username": username})


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            return render(request, "register.html", {"error": "Passwords do not match"})

        existing_user = User.objects.filter(username=username).exists()
        if existing_user:
            return render(
                request, "register.html", {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username,
            password=password,
        )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("profile", username=username)
        else:
            return render(
                request,
                "register.html",
                {"error": "Failed to log in. Please try again."},
            )

    return render(request, "register.html", context={})
