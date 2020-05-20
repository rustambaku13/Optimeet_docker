from google.cloud import language

from google.cloud.language import enums
from google.cloud.language import types
import csv
# Instantiates a client
client = language.LanguageServiceClient()
# export GOOGLE_APPLICATION_CREDENTIALS="/Users/rustamquliyev/Documents/Optify/Optify_App/Django-backend/optify/optify-a768f9fd8bc9.json"

with open('schedule_data.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    for row in csv_reader:      
        text = row[0]         
        document = types.Document(
        content=text,
        language="en",
        type=enums.Document.Type.PLAIN_TEXT) 
        response = client.analyze_syntax(
            document=document
        )   
        print(response)
       
    # Get the language of the text, which will be the same as
    # the language specified in the request or, if not specified,
    # the automatically-detected language.
               




#Entity Analyss


# Detects the sentiment of the text
# sentiment = client.analyze_sentiment(document=document).document_sentiment

# print('Text: {}'.format(text))
# print('Sentiment: {}, {}'.format(sentiment.score, sentiment.magnitude))