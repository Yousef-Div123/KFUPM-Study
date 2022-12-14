from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import SubjectsSerializer,AnswerSerializerAll, TestsSerializer, AnswerSerializer,QuestionSerializer, TestSerializer
from .models import Subject, Test, Question, Answer, Score

# Create your views here.

@api_view(['GET'])
def getSubjects(request):
    subjects = Subject.objects.all()
    serializer = SubjectsSerializer(subjects, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getTests(request, subject):
    subject = Subject.objects.get(name = subject)
    test = Test.objects.filter(subject = subject)
    serializer = TestsSerializer(test, many = True)
    for test in serializer.data:
        test['picture'] = str(subject.picture)
    return Response(serializer.data)

class GetTest(APIView):
    def get(self, request, test):
        test = Test.objects.get(title = test)
        Tserializer = TestSerializer(test)
        data = Tserializer.data

        questions = []
        for question in data['questions']:
            q = Question.objects.get(id = question)
            serializer = QuestionSerializer(q).data
            answer = Answer.objects.get(question = q)
            answers = AnswerSerializer(answer)
            
            serializer["answers"] = answers.data
            
            questions.append(serializer)

            
               
        data["questions"] = questions  


        return Response(data)


class TakeTest(APIView):
    def post(self, request):
        user = request.user
        test = Test.objects.get(title = request.data['title'])

        user_score = 0
        res = {}
        res['test_score'] = test.score
        res['title'] = test.title
        res_questions = []
        for q in request.data['questions']:
            res_question = {}
            question = Question.objects.get(id = q['id'])
            answers = Answer.objects.get(question = question)
            answers_serializer = AnswerSerializerAll(answers)

            res_question['id'] = question.id
            res_question['question_body'] = question.question_body
            res_question['answers'] = answers_serializer.data
            res_question['answers']['user_answer'] = q['answer']
            
            if q['answer'] == answers.correct_answer:
                user_score += 1

            res_questions.append(res_question)

        res['questions'] = res_questions
        res['user_score'] = user_score

        score = Score.objects.create(student = user, test = test, user_score = user_score)
        score.save()

        return Response(res)        
            




        