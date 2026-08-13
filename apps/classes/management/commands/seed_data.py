from django.core.management.base import BaseCommand
from apps.classes.models import Grade, Section

class Command(BaseCommand):
    help = 'Seed grades and sections'

    def handle(self, *args, **kwargs):
        # Create Grades 1-10
        grades = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        for g in grades:
            Grade.objects.get_or_create(grade_name=g)
        self.stdout.write(self.style.SUCCESS('✅ Grades created'))
        
        # Create Sections A, B, C
        sections = ['A', 'B', 'C']
        for s in sections:
            Section.objects.get_or_create(section_name=s)
        self.stdout.write(self.style.SUCCESS('✅ Sections created'))