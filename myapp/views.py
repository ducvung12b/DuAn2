from django.shortcuts import get_object_or_404, render,redirect
import os
from django.http import HttpResponse,JsonResponse
from .models import *
import json
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# LogIn LogOut
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError  
from .forms import CommentForm
from django.db.models import Avg


# Create your views here.

#Home
@login_required
def home(request):
    
    recipes = Recipe.objects.all()
    recipeimage = RecipeImage.objects.all()
    return render(request,'myapp/home.html', {'recipes': recipes,'recipeimage':recipeimage})

#-------------------------MyPOST-------------------------

@login_required
def mypost(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request,'myapp/mypost.html', {'recipes': recipes})
@login_required
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    recipe.delete()
    return redirect('mypost')
    

#-------------------------POST-------------------------

@login_required
def postpage(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        classify = request.POST.getlist('classify')
        
        introduce = request.POST.get('introduce')
        description = request.POST.get('description')
        images = request.FILES.getlist('images')
        if title and description:
            # Tạo công thức nấu ăn mới
            recipe = Recipe.objects.create(
                title=title,
                classify = classify,
                description=description,
                introduce=introduce,
                author=request.user
            )
            # Lưu từng ảnh liên kết với công thức nấu ăn
            for image in images:
                RecipeImage.objects.create(recipe=recipe, image=image)
            return redirect('mypost')  # Chuyển hướng đến danh sách công thức
        else:
            error = "Bạn cần nhập đầy đủ tiêu đề và mô tả."
            return render(request, 'myapp/postpage.html', {'error': error})
    return render(request, 'myapp/postpage.html')


#-------------------------LIKE-------------------------

@login_required
def savelike(request):
    if request.user.is_authenticated:
        liked_recipes = request.user.liked_recipes.all()  # Lấy danh sách công thức người dùng đã thích
        recipes = Recipe.objects.all()
        recipeimage = RecipeImage.objects.all()
        return render(request, 'myapp/savelike.html', {'liked_recipes': liked_recipes,'recipes': recipes,'recipeimage':recipeimage,})
    return redirect('login')  # Yêu cầu đăng nhập nếu chưa đăng nhập

@login_required
def like_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user.is_authenticated:
        recipe.liked_tym.add(request.user)  # Thêm người dùng vào danh sách yêu thích
    return redirect('home')  # Quay lại trang chủ sau khi bấm yêu thích

def unlike_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.user.is_authenticated:
        recipe.liked_tym.remove(request.user)  # Xóa người dùng khỏi danh sách yêu thích
    return redirect('savelike')  # Quay lại trang savelike sau khi xóa


#-------------------------DETAIL-------------------------

@login_required
def detail(request,recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.views += 1  # Tăng số lượt xem lên 1
    recipe.save()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            if parent_id:  # Nếu có parent_id, đây là một reply
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return redirect('detail', recipe_id=recipe_id)
    else:
        form = CommentForm()
    comments = recipe.comments.filter(parent__isnull=True)  # Chỉ hiển thị bình luận gốc, không phải reply
    images = RecipeImage.objects.filter(recipe=recipe)  # Lấy tất cả ảnh của công thức này 
    total_count = comments.count() + Comment.objects.filter(parent__in=comments).count()

    # if images.count() > 4:
    #     raise ValidationError("Chỉ Đăng tối đa 4 ảnh.")
    
    return render(request,'myapp/detail.html', 
        {'recipe': recipe, 
        'images': images,
        'recipe': recipe,
        'comments': comments,
        'form': form,
        'total_count': total_count,})


#-------------------------EDIT-------------------------
@login_required
def edit_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    images = RecipeImage.objects.filter(recipe=recipe)

    if request.method == "POST":
        # Cập nhật thông tin công thức
        title = request.POST.get("title")
        introduce = request.POST.get("introduce")
        description = request.POST.get("description")
        recipe.title = title
        recipe.introduce = introduce
        recipe.description = description

        # Xử lý việc lưu phân loại
        classify = request.POST.getlist('classify')  # Lấy danh sách các phân loại được chọn
        recipe.classify = classify
        recipe.save()

        # Xử lý việc tải lên nhiều ảnh
        if request.FILES.getlist('images'):
            for image_file in request.FILES.getlist('images'):
                RecipeImage.objects.create(recipe=recipe, image=image_file)

        # Xóa ảnh đã chọn
        delete_image_ids = request.POST.getlist('delete_images')
        if delete_image_ids:
            RecipeImage.objects.filter(id__in=delete_image_ids, recipe=recipe).delete()

        return redirect('mypost')  # Điều hướng tới trang mong muốn
    return render(request, 'myapp/edit.html', {'recipe': recipe, 'images': images})

#-------------------------LOGIN_OUT-------------------------

def logoutPage(request):
    logout(request)
    return redirect('viewhome')

def loginPage(request):
    if request.user.is_authenticated:
        if request.user.is_staff:  # Kiểm tra nếu người dùng là admin
            return redirect('ad')  # Điều hướng đến trang admin
        else:
            return redirect('home')  # Điều hướng đến trang chủ người dùng
 
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if user.is_staff:  # Nếu người dùng là admin
                return redirect('ad')  # Điều hướng đến trang admin
            else:
                return redirect('home')  # Điều hướng đến trang chủ người dùng
        else:
            messages.info(request, 'Tài Khoản Đăng Nhập Chưa Đúng..!')

    context = {}
    return render(request, 'myapp/login.html', context)


#-------------------------REGISTER-------------------------

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 == password2:
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'register.html', {'Lỗi': 'Mật Khẩu Không Trùng Khớp'})
    return render(request,'myapp/register.html')

#-------------------------SHEARCH-------------------------
def search(request):
    if request.method == 'POST':
        searched = request.POST['searched']
        checks = Recipe.objects.filter(title__contains = searched)
    recipe = Recipe.objects.all()
    return render(request, 'myapp/search.html', {'recipe':recipe,'searched': searched, 'checks': checks})


#-------------------------RATING-------------------------
@login_required
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if request.method == 'POST':
        try:
            stars = int(request.POST.get('stars', 0))  # Mặc định là 0 nếu không có đánh giá
            if stars < 0 or stars > 5:
                raise ValueError("Số sao không hợp lệ")
        except ValueError:
            return render(request, 'rate_recipe.html', {'recipe': recipe, 'error': 'Đánh giá không hợp lệ. Vui lòng chọn từ 1 đến 5 sao.'})
        
        # Cập nhật hoặc tạo mới đánh giá
        rating, created = Rating.objects.update_or_create(
            user=request.user,
            recipe=recipe,
            defaults={'stars': stars},)
        return redirect('detail', recipe_id=recipe.id)
    return render(request, 'rate_recipe.html', {'recipe': recipe})

@login_required
def reset_rating(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    
    # Tìm và xóa đánh giá của người dùng hiện tại
    rating = Rating.objects.filter(user=request.user, recipe=recipe).first()
    if rating:
        rating.delete()  # Xóa đánh giá của người dùng
        
        # Tính lại điểm trung bình mới
        new_average = Rating.objects.filter(recipe=recipe).aggregate(avg_rating=Avg('stars'))['avg_rating']
        
        # Nếu không có đánh giá nào thì đặt giá trị trung bình về 0
        if new_average is None:
            new_average = 0
        
        return JsonResponse({'message': 'Bạn đã hủy đánh giá thành công!', 'average_rating': new_average}, status=200)

    return JsonResponse({'error': 'Không tìm thấy đánh giá để reset.'}, status=400)


#-------------------------FILTER-------------------------
@login_required
def rating_recipes(request):
    # Lọc và sắp xếp các công thức có điểm đánh giá cao nhất  
    recipes = sorted(Recipe.objects.all(), key=lambda r: r.average_rating, reverse=True)
    context = {
        'recipes': recipes,
    }
    return render(request, 'myapp/filter_rating.html', context)

@login_required
def view_recipes(request):
    # Lọc và sắp xếp các công thức có lượt xem cao nhất
    recipes = Recipe.objects.all().order_by('-views')
    context = {
        'recipes': recipes,
    }
    return render(request, 'myapp/filter_view.html', context)





#-------------------------ADMIN-------------------------


@login_required
def users(request):
    users = User.objects.all()
    return render(request, 'admin/users.html', {'users': users})

def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    messages.success(request, 'Tài khoản đã được xóa thành công.')
    return redirect('users')






@login_required
def admin_app(request):
    
    if request.user.is_staff:
        recipes = Recipe.objects.all()
        recipeimage = RecipeImage.objects.all()
        return render(request,'admin/admin.html', {'recipes': recipes,'recipeimage':recipeimage})
    else:
        return redirect('home')

@login_required   
def admin_delete(request, post_id):
    if request.user.is_staff:
        post = get_object_or_404(Recipe, id=post_id)
        post.delete()
        messages.success(request, 'Đã xoá bài post thành công.')
    return redirect('ad')  # Thay 'admin_dashboard' bằng tên URL của trang admin bạn

@login_required
def admin_edit(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id,)
    images = RecipeImage.objects.filter(recipe=recipe)
    if request.user.is_staff:
        if request.method == 'POST':
                title = request.POST.get("title")
                introduce = request.POST.get("introduce")
                description = request.POST.get("description")
                recipe.title = title
                recipe.introduce = introduce
                recipe.description = description

                # Xử lý việc lưu phân loại
                classify = request.POST.getlist('classify')  # Lấy danh sách các phân loại được chọn
                recipe.classify = classify
                recipe.save()

                # Xử lý việc tải lên nhiều ảnh
                if request.FILES.getlist('images'):
                    for image_file in request.FILES.getlist('images'):
                        RecipeImage.objects.create(recipe=recipe, image=image_file)

                # Xóa ảnh đã chọn
                delete_image_ids = request.POST.getlist('delete_images')
                if delete_image_ids:
                    RecipeImage.objects.filter(id__in=delete_image_ids, recipe=recipe).delete()

                return redirect('ad')  # Điều hướng tới trang mong muốn
        return render(request, 'admin/adminedit.html', {'recipe': recipe, 'images': images})
    



@login_required
def addetail(request,recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    recipe.views += 1  # Tăng số lượt xem lên 1
    recipe.save()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            parent_id = request.POST.get('parent_id')
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.user = request.user
            if parent_id:  # Nếu có parent_id, đây là một reply
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            return redirect('addetail', recipe_id=recipe_id)
    else:
        form = CommentForm()
    comments = recipe.comments.filter(parent__isnull=True)  # Chỉ hiển thị bình luận gốc, không phải reply
    images = RecipeImage.objects.filter(recipe=recipe)  # Lấy tất cả ảnh của công thức này 
    total_count = comments.count() + Comment.objects.filter(parent__in=comments).count()

    # if images.count() > 4:
    #     raise ValidationError("Chỉ Đăng tối đa 4 ảnh.")
    
    return render(request,'admin/addetail.html', 
        {'recipe': recipe, 
        'images': images,
        'recipe': recipe,
        'comments': comments,
        'form': form,
        'total_count': total_count,})

@login_required
def addelete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    recipe = comment.recipe  # Lấy sản phẩm chứa bình luận

    # Xóa comment ngay lập tức
    comment.delete()
    messages.success(request, "Bình luận đã được xóa thành công.")
    
    # Điều hướng về trang chi tiết sản phẩm sau khi xóa
    return redirect('addetail', recipe_id=recipe.id)


# ----------------MYADMIN------------------
@login_required
def myadmin(request):
    recipes = Recipe.objects.filter(author=request.user)
    return render(request,'admin/myadmin.html', {'recipes': recipes})

@login_required
def admin_myrecipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id, author=request.user)
    recipe.delete()
    return redirect('myadmin')







@login_required
def search_user(request):
    query = request.GET.get('query')
    users = User.objects.filter(username__icontains=query) if query else []
    return render(request, 'admin/search_user.html', {'users': users, 'query': query})


#-------------------------VIEW-------------------------
def viewhome(request):
    recipes = Recipe.objects.all()
    recipeimage = RecipeImage.objects.all()
    return render(request,'myapp/viewhome.html', {'recipes': recipes,'recipeimage':recipeimage})





def recipes_by_classify(request, classify):
    # Lấy tất cả công thức theo phân loại
    if classify not in dict(Recipe.CLASSIFY_CHOICES).keys():
        return render(request, 'myapp/error.html', {'message': 'Invalid classify'})

    recipes = Recipe.objects.filter(classify=classify)
    context = {
        'recipes': recipes,
        'classify': classify,
    }
    return render(request, 'myapp/recipes_by_classify.html', context)