from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = '/api/monitor/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)