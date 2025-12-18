from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import LoginForm, ProductForm
from .models import Order, Product, Supplier, UserProfile, UserRole


def _get_user_role(user) -> str:
    if isinstance(user, AnonymousUser):
        return UserRole.GUEST
    try:
        return user.profile.role
    except UserProfile.DoesNotExist:
        return UserRole.CLIENT


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("shop:product_list")

    form = LoginForm(request=request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("shop:product_list")

    return render(
        request,
        "shop/login.html",
        {
            "form": form,
        },
    )


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("shop:login")


def product_list_guest(request: HttpRequest) -> HttpResponse:
    products = Product.objects.select_related(
        "category",
        "manufacturer",
        "supplier",
    ).all()
    context = {
        "products": products,
        "role": UserRole.GUEST,
        "user_full_name": "Гость",
        "show_filters": False,
    }
    return render(request, "shop/product_list.html", context)


@login_required
def product_list(request: HttpRequest) -> HttpResponse:
    role = _get_user_role(request.user)
    products = Product.objects.select_related(
        "category",
        "manufacturer",
        "supplier",
    ).all()

    show_filters = role in (UserRole.MANAGER, UserRole.ADMIN)

    suppliers = None
    if show_filters:
        suppliers = Supplier.objects.all().order_by("name")
        supplier_id = request.GET.get("supplier")
        ordering = request.GET.get("ordering")
        search = request.GET.get("search")

        if supplier_id:
            products = products.filter(supplier_id=supplier_id)

        if search:
            products = products.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(category__name__icontains=search)
                | Q(manufacturer__name__icontains=search)
                | Q(supplier__name__icontains=search)
            )

        if ordering == "stock_asc":
            products = products.order_by("stock_quantity")
        elif ordering == "stock_desc":
            products = products.order_by("-stock_quantity")

    context = {
        "products": products,
        "role": role,
        "user_full_name": getattr(
            getattr(request.user, "profile", None),
            "full_name",
            request.user.get_username(),
        ),
        "show_filters": show_filters,
        "suppliers": suppliers,
    }
    return render(request, "shop/product_list.html", context)


def _require_admin(request: HttpRequest) -> str | None:
    role = _get_user_role(request.user)
    if role != UserRole.ADMIN:
        messages.error(request, "У вас нет прав для выполнения этого действия.")
        return "shop:product_list"
    return None


@login_required
def product_create(request: HttpRequest) -> HttpResponse:
    redirect_name = _require_admin(request)
    if redirect_name:
        return redirect(redirect_name)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Товар успешно добавлен.")
            return redirect("shop:product_list")
    else:
        form = ProductForm()
    return render(
        request,
        "shop/product_form.html",
        {
            "form": form,
            "title": "Добавление товара",
        },
    )


@login_required
def product_update(request: HttpRequest, pk: int) -> HttpResponse:
    redirect_name = _require_admin(request)
    if redirect_name:
        return redirect(redirect_name)

    product = get_object_or_404(Product, pk=pk)
    old_image = product.image.path if product.image else None

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            # удаляем старое фото, если загружено новое
            if old_image and product.image and product.image.path != old_image:
                from pathlib import Path

                old_path = Path(old_image)
                if old_path.exists():
                    old_path.unlink()
            messages.success(request, "Товар успешно изменён.")
            return redirect("shop:product_list")
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "shop/product_form.html",
        {
            "form": form,
            "title": f"Редактирование товара #{product.pk}",
            "product": product,
        },
    )


@login_required
def product_delete(request: HttpRequest, pk: int) -> HttpResponse:
    redirect_name = _require_admin(request)
    if redirect_name:
        return redirect(redirect_name)

    product = get_object_or_404(Product, pk=pk)

    if product.order_items.exists():
        messages.error(
            request,
            "Нельзя удалить товар, который присутствует в заказах.",
        )
        return redirect("shop:product_list")

    if request.method == "POST":
        product.delete()
        messages.success(request, "Товар удалён.")
        return redirect("shop:product_list")

    return render(
        request,
        "shop/product_confirm_delete.html",
        {
            "product": product,
        },
    )


@login_required
def order_list(request: HttpRequest) -> HttpResponse:
    role = _get_user_role(request.user)
    if role not in (UserRole.MANAGER, UserRole.ADMIN):
        messages.error(request, "У вас нет прав для просмотра заказов.")
        return redirect("shop:product_list")

    orders = (
        Order.objects.select_related("customer")
        .prefetch_related("items__product")
        .all()
    )
    return render(
        request,
        "shop/order_list.html",
        {
            "orders": orders,
            "role": role,
            "user_full_name": getattr(
                getattr(request.user, "profile", None),
                "full_name",
                request.user.get_username(),
            ),
        },
    )


