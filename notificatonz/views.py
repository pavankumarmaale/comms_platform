from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import MessageLog
from .services.providers import send_message
from .forms import MessageForm

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

@login_required
def send_message_console(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.user = request.user
            
            # Use the communication service
            result = send_message(
                channel=message.channel,
                recipient=message.recipient,
                subject=message.subject,
                body=message.body
            )
            
            if result['status'] == 'success':
                message.status = 'SENT'
                messages.success(request, f"Message sent successfully via {result.get('provider', 'service')}!")
            else:
                message.status = 'FAILED'
                messages.error(request, f"Failed to send: {result.get('error', 'Unknown error')}")
            
            message.save()
            return redirect('dashboard')
    else:
        form = MessageForm()
    
    return render(request, 'core/console.html', {'form': form})

@login_required
def dashboard(request):
    history = MessageLog.objects.filter(user=request.user).order_by('-created_at')
    total = history.count()
    sent = history.filter(status='SENT').count()
    pending = history.filter(status='PENDING').count()
    failed = history.filter(status='FAILED').count()
    return render(request, 'core/dashboard.html', {
        'messages': history,
        'total_messages': total,
        'sent_count': sent,
        'pending_count': pending,
        'failed_count': failed
    })