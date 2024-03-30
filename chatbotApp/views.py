import os
import sys

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt


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
def chat_view(request):
    PERSIST = False
    import pdb
    
    if request.method == 'POST':
        user_message = request.POST.get('message', '')
        # pdb.set_trace()
        

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
            pdb.set_trace()
            # print(result['answer'])
            chatbot_response = result['answer']

            return JsonResponse({'response': chatbot_response})

            chat_history.append((query, result['answer']))
            query = None

    # Return dates

    return render(request, 'chat.html')
