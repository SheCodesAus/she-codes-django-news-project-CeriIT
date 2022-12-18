from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views import generic
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import NewsStory
from .forms import StoryForm, FilterForm


User = get_user_model()
class IndexView(generic.ListView):
    template_name = 'news/index.html'
    context_object_name = 'all_stories'

    def get_queryset(self):
        '''Return all news stories.'''
        qs = NewsStory.objects.all()

        form = FilterForm(self.request.GET)
        order_by = "-pub_date"

        if form.is_valid():
            #order
            order = form.cleaned_data.get('order')
            if order == "oldfirst":
                order_by = "pub_date"

            #author
            if author := form.cleaned_data.get('author'):
                qs=qs.filter(author=author)

            #search
            if search := form.cleaned_data.get('search'): 
                qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search))

        #filter
        # if search := self.request.GET.get('search'): #.get allows it to be empty. := assign if doesn't exist
        #     qs = qs.filter(Q(title__icontains=search) | Q(content__icontains=search)) #Q allows combining filter on both title and content

        # #authored by
        # if author := self.request.GET.get('author'):
        #     qs=qs.filter(author=author)

        # #ordering
        # order = self.request.GET.get('order')
        # if order == "oldfirst":
        #     order_by = "pub_date"
        # else:
        #     order_by = "-pub_date"       

        return qs.order_by(order_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['latest_stories'] = NewsStory.objects.all().order_by('-pub_date').values()[:4]
        # context['all_stories'] = NewsStory.objects.all()
        # context['author_list'] = User.objects.all()
        context['form'] = FilterForm(self.request.GET)
        return context

class StoryView(generic.DetailView):
    model = NewsStory
    template_name = 'news/story.html'  #default: news/newsstory_detail.html
    context_object_name = 'story'  #default: newsstory


class AddStoryView(generic.CreateView):
    form_class = StoryForm
    context_object_name = 'storyForm' 
    template_name = 'news/createStory.html'  #default to newsstory_form.html
    success_url = reverse_lazy('news:index')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AuthorView(generic.ListView):
    template_name = 'news/author.html'

    def get_queryset(self):
        '''Return all news stories.'''
        return NewsStory.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_stories'] = NewsStory.objects.all().order_by('-pub_date').values()
        return context

class StoryEditView(generic.UpdateView):
    model = NewsStory
    fields = ["title",
        "content",
        "img_url"
    ] 
    # fields = __all__  # to include all fields
    # form_class = StoryForm  #use the same form as AddStoryView

    #redirect back to the story being edited
    def get_success_url(self):
        return reverse_lazy('news:story', kwargs={"pk":self.kwargs['pk']})

    #only allow the author to change the story
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            raise qs.model.DoesNotExist
        qs = qs.filter(author=self.request.user)
        return qs

class DeleteView(LoginRequiredMixin, generic.DeleteView):
    model = NewsStory
    template_name = 'news/delete.html' #defaults to newsstory_confirm_delete.html

    #only allow the author to change the story (with django built-in function LoginRequiredMixIn)
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)

#like functionality without views. this is typically done in javascript
@login_required
def like(request, pk):
    """"when given a pk for a newsstory, add the user to the like, or if exists, remove the user"""
    news_story = get_object_or_404(NewsStory, pk=pk)
    if news_story.favourited_by.filter(username=request.user.username).exists():
        news_story.favourited_by.remove(request.user)
    else:
        news_story.favourited_by.add(request.user)
    return redirect(reverse_lazy('news:story', kwargs={'pk':pk}))

