from .forms import CustomUserCreationForm
from django.views.generic.edit import FormView


class RegisterView(FormView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = '/api/monitor/'

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
