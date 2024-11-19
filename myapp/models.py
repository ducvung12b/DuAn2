from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse
# Create your models here.
 
#Form register
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','first_name','last_name','password1','password2']

class Recipe(models.Model):
    title = models.CharField(max_length=100,null=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    introduce =  models.CharField(max_length=100,null=True)
    description = models.CharField(max_length=200,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.IntegerField(default=0)
    liked_tym = models.ManyToManyField(User, related_name='liked_recipes', blank=True)
    average_rating = models.FloatField(default=0) 
    CLASSIFY_CHOICES = [
            ('Mặn', 'Mặn'),
            ('Chay', 'Chay'),
            ('Kiên', 'Kiên'),
            ('Béo', 'Béo'),
        ]
    classify = models.CharField(max_length=10, choices=CLASSIFY_CHOICES)

    
    def __str__(self):
            return self.title
    
    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return round(sum(rating.stars for rating in ratings) / ratings.count(), 2)
        return 0
    

class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ảnh Của Bài : {self.recipe.title}"



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"

    def is_reply(self):
        return self.parent is not None
    


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('user', 'recipe')  # Đảm bảo mỗi người dùng chỉ đánh giá một công thức một lần

    def __str__(self):
        return f'{self.user} rated {self.recipe} with {self.stars} stars'