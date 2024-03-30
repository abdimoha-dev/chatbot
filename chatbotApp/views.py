import os
import sys

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

from  .constants import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

@csrf_exempt
@login_required(login_url='login')
def chat_view(request):
    PERSIST = False
    import pdb
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '')

        query = user_message
        # if len(sys.argv) > 1:
        #     query = sys.argv[1]

        if PERSIST and os.path.exists("persist"):
            print("Reusing index...\n")
            vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
            index = VectorStoreIndexWrapper(vectorstore=vectorstore)
        else:
        #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            loader = DirectoryLoader(os.path.join(BASE_DIR, "data"))
            if PERSIST:
                index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
            else:
                index = VectorstoreIndexCreator().from_loaders([loader])

        chain = ConversationalRetrievalChain.from_llm(
        llm=ChatOpenAI(model="gpt-3.5-turbo"),
        retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
        )

        chat_history = []
        while True:
            if not query:
                query = input("Prompt: ")
            if query in ['quit', 'q', 'exit']:
                sys.exit()
            result = chain({"question": query, "chat_history": chat_history})
            # pdb.set_trace()
            # print(result['answer'])
            chatbot_response = result['answer']

            return JsonResponse({'response': chatbot_response})

            chat_history.append((query, result['answer']))
            query = None

    # Return dates

    return render(request, 'chat.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        # import pdb
        # pdb.set_trace()
        if user is not None:
            login(request, user)
            messages.success(request, 'logged in successfully')
            return redirect('chatbot')
        else:
            messages.success(request, 'Incorect username/password')
            return redirect('login')

    else:  # Get method ->
        # check if test user exists
        User = get_user_model()
        if User.objects.filter(username='test').exists():
            return render(request, 'login.html')
        # if test user does not exist, create user
        else:
            user = User.objects.create_user(
                first_name='test',
                last_name='user',
                username='test',
                password='test',
                email='test@covid.com',
                is_staff=True,
                is_admin=True,
            )
            user.save()
            return render(request, 'login.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request, 'logged out successfully!')
    return redirect('login')

@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST' and request.FILES['document']:
        document = request.FILES['document']
        # Define the directory where you want to save the uploaded file
        upload_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
        # Create the directory if it doesn't exist
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        # Construct the file path
        file_path = os.path.join(upload_dir, document.name)
        # Write the uploaded file to the specified location
        with open(file_path, 'wb') as destination:
            for chunk in document.chunks():
                destination.write(chunk)
        # Optionally, you can save the file path in your database
        # For example:
        # UploadedFile.objects.create(file_path=file_path)
        return render(request, 'upload.html')
    return render(request, 'upload.html')
