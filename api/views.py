from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Company, KBEntry, QueryLog
from .permissions import IsAdminUser


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        company_name = request.data.get('company_name')
        email = request.data.get('email')

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password, email=email)
        company = user.company
        company.company_name = company_name
        company.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'username': user.username,
            'company_name': company.company_name,
            'api_key': company.api_key,
            'access': str(refresh.access_token),
        }, status=201)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Invalid username or password'}, status=401)

        refresh = RefreshToken.for_user(user)
        company = user.company

        return Response({
            'access': str(refresh.access_token),
            'company_name': company.company_name,
            'api_key': company.api_key,
        })


class KBQueryView(APIView):
    def post(self, request):
        search_term = request.data.get('search', '').strip()
        if not search_term:
            return Response({'error': 'search is required'}, status=400)

        with transaction.atomic():
            entries = KBEntry.objects.filter(
                Q(question__icontains=search_term) | Q(answer__icontains=search_term)
            )
            count = entries.count()
            QueryLog.objects.create(
                company=request.user.company,
                search_term=search_term,
                results_count=count
            )

        results = [
            {
                'id': str(entry.id),
                'question': entry.question,
                'answer': entry.answer,
                'category': entry.category,
            }
            for entry in entries
        ]

        return Response({
            'search': search_term,
            'count': count,
            'results': results,
        })


class UsageSummaryView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_queries = QueryLog.objects.aggregate(total=Count('id'))['total']
        active_companies = QueryLog.objects.values('company').distinct().count()
        top_terms = QueryLog.objects.values('search_term').annotate(count=Count('id')).order_by('-count')[:5]

        return Response({
            'total_queries': total_queries,
            'active_companies': active_companies,
            'top_search_terms': list(top_terms),
        })
