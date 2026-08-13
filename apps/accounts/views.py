from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from .models import User
from .forms import LoginForm, UserCreationForm


# ==================== AUTHENTICATION VIEWS ====================

def login_view(request):
    """Login view for all users (Principal & Teacher)"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').strip()
            password = form.cleaned_data.get('password')
            
            # Check for uppercase and show error
            if username != username.lower():
                messages.error(request, 'Username must be in lowercase only! Use small letters.')
            else:
                user = authenticate(username=username.lower(), password=password)
                
                if user is not None:
                    if user.status == 'Active':
                        login(request, user)
                        messages.success(request, f'Welcome back, {user.get_full_name()}!')
                        return redirect('dashboard')
                    else:
                        messages.error(request, 'Your account is inactive. Contact administrator.')
                else:
                    messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout view"""
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


# ==================== USER MANAGEMENT VIEWS ====================

@method_decorator(login_required, name='dispatch')
class UserListView(ListView):
    """List all users (Principal only)"""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied. Principal only.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


@method_decorator(login_required, name='dispatch')
class UserCreateView(SuccessMessageMixin, CreateView):
    """Create new user (Principal only)"""
    model = User
    form_class = UserCreationForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('user_list')
    success_message = 'User created successfully!'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_principal:
            messages.error(request, 'Access denied. Principal only.')
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)


# ==================== PROFILE VIEWS ====================

@login_required
def profile_view(request):
    """View and edit profile"""
    if request.method == 'POST':
        user = request.user
        
        # Update username
        new_username = request.POST.get('username', '').strip()
        if new_username and new_username != user.username:
            # Check for uppercase letters
            if new_username != new_username.lower():
                messages.error(request, 'Username must be in lowercase only! Use small letters.')
            elif User.objects.filter(username=new_username).exists():
                messages.error(request, 'Username already taken!')
            else:
                old_username = user.username
                user.username = new_username.lower()
                user.save()
                messages.success(request, f'Username changed from {old_username} to {new_username.lower()}!')
        
        # Update email
        new_email = request.POST.get('email', '').strip()
        if new_email and new_email != user.email:
            user.email = new_email
            user.save()
            messages.success(request, 'Email updated!')
        
        # Update name
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        if first_name != user.first_name or last_name != user.last_name:
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            messages.success(request, 'Name updated!')
        
        return redirect('profile')
    
    return render(request, 'accounts/profile.html')


@login_required
def change_password_view(request):
    """Change password only - separate form"""
    if request.method == 'POST':
        user = request.user
        old_password = request.POST.get('old_password', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        # Validate all fields are filled
        if not old_password or not new_password or not confirm_password:
            messages.error(request, 'All password fields are required.')
            return redirect('profile')
        
        # Check current password
        if not user.check_password(old_password):
            messages.error(request, 'Current password is incorrect!')
            return redirect('profile')
        
        # Check passwords match
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match!')
            return redirect('profile')
        
        # Check minimum length
        if len(new_password) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
            return redirect('profile')
        
        # Change password and keep user logged in
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully!')
    
    return redirect('profile')