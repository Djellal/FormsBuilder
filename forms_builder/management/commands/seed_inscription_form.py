from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from forms_builder.models import Form, FormField, FormStatus, FormAccess, FormType, FieldType


class Command(BaseCommand):
    help = 'Seed the inscription form with all required fields'

    def handle(self, *args, **options):
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        form, created = Form.objects.get_or_create(
            slug='inscription-master',
            defaults={
                'title': 'Inscription Master',
                'description': 'Formulaire d\'inscription pour les études de Master',
                'form_type': FormType.REGISTRATION,
                'status': FormStatus.PUBLISHED,
                'access_level': FormAccess.AUTHENTICATED,
                'allow_update': True,
                'single_submission': True,
                'created_by': admin_user,
            }
        )

        if not created:
            form.fields.all().delete()
            self.stdout.write(self.style.WARNING('Form already exists. Recreating fields...'))

        fields_data = [
            {'name': 'etab_id', 'label': 'Établissement', 'field_type': FieldType.SELECT_ETABLISSEMENT, 'is_required': True},
            {'name': 'nom', 'label': 'Nom', 'field_type': FieldType.TEXT, 'is_required': True},
            {'name': 'prenom', 'label': 'Prénom', 'field_type': FieldType.TEXT, 'is_required': True},
            {'name': 'date_naissance', 'label': 'Date de Naissance', 'field_type': FieldType.DATE, 'is_required': True},
            {'name': 'lieu_naissance', 'label': 'Lieu de Naissance', 'field_type': FieldType.TEXT, 'is_required': True},
            {'name': 'tel', 'label': 'Téléphone', 'field_type': FieldType.PHONE, 'is_required': True},
            {'name': 'origine_filiere', 'label': 'Filière d\'Origine', 'field_type': FieldType.TEXT, 'is_required': True},
            {'name': 'origine_specialite', 'label': 'Spécialité d\'Origine', 'field_type': FieldType.TEXT, 'is_required': True},
            {'name': 'annee_diplome', 'label': 'Année du Diplôme', 'field_type': FieldType.NUMBER, 'is_required': True, 'placeholder': 'Ex: 2024'},
            {'name': 'annee_bac', 'label': 'Année du Bac', 'field_type': FieldType.NUMBER, 'is_required': True, 'placeholder': 'Ex: 2020'},
            {'name': 'num_bac', 'label': 'Numéro du Bac', 'field_type': FieldType.TEXT, 'is_required': True},
            {
                'name': 'system_suivi',
                'label': 'Système Suivi',
                'field_type': FieldType.SELECT,
                'is_required': True,
                'options_json': ['LMD', 'Classique4', 'Classique5', 'SciencesMedicales']
            },
            {'name': 'moyenne_1ere_annee', 'label': 'Moyenne 1ère Année', 'field_type': FieldType.NUMBER, 'is_required': True, 'placeholder': 'Ex: 12.50'},
            {'name': 'moyenne_2eme_annee', 'label': 'Moyenne 2ème Année', 'field_type': FieldType.NUMBER, 'is_required': True, 'placeholder': 'Ex: 13.00'},
            {'name': 'moyenne_3eme_annee', 'label': 'Moyenne 3ème Année', 'field_type': FieldType.NUMBER, 'is_required': False, 'placeholder': 'Ex: 14.25'},
            {'name': 'moyenne_4eme_annee', 'label': 'Moyenne 4ème Année', 'field_type': FieldType.NUMBER, 'is_required': False, 'placeholder': 'Ex: 15.00'},
            {'name': 'moyenne_5eme_annee', 'label': 'Moyenne 5ème Année', 'field_type': FieldType.NUMBER, 'is_required': False, 'placeholder': 'Ex: 14.75'},
            {'name': 'moyenne_6eme_annee', 'label': 'Moyenne 6ème Année', 'field_type': FieldType.NUMBER, 'is_required': False, 'placeholder': 'Ex: 15.50'},
            {'name': 'nbr_redoublements', 'label': 'Nombre de Redoublements', 'field_type': FieldType.NUMBER, 'is_required': True, 'default_value': '0'},
            {'name': 'nbr_admissions_dettes', 'label': 'Nombre d\'Admissions avec Dettes', 'field_type': FieldType.NUMBER, 'is_required': True, 'default_value': '0'},
            {'name': 'nbr_admissions_rattrapage', 'label': 'Nombre d\'Admissions après Rattrapage', 'field_type': FieldType.NUMBER, 'is_required': True, 'default_value': '0'},
            {'name': 'pieces_jointes', 'label': 'Pièces Jointes', 'field_type': FieldType.FILE, 'is_required': True},
            {
                'name': 'niveau_demande',
                'label': 'Niveau Demandé',
                'field_type': FieldType.SELECT,
                'is_required': True,
                'options_json': ['Licence', 'M1', 'M2']
            },
            {'name': 'domaine', 'label': 'Domaine', 'field_type': FieldType.SELECT_DOMAINE, 'is_required': True},
            {'name': 'voeux1', 'label': 'Vœu 1 (Spécialité)', 'field_type': FieldType.SELECT_SPECIALITE, 'is_required': True},
            {'name': 'voeux2', 'label': 'Vœu 2 (Spécialité)', 'field_type': FieldType.SELECT_SPECIALITE, 'is_required': False},
            {'name': 'voeux3', 'label': 'Vœu 3 (Spécialité)', 'field_type': FieldType.SELECT_SPECIALITE, 'is_required': False},
            {'name': 'traite', 'label': 'Traité', 'field_type': FieldType.HIDDEN, 'is_required': False, 'default_value': 'false'},
            {'name': 'accepte', 'label': 'Accepté', 'field_type': FieldType.HIDDEN, 'is_required': False, 'default_value': 'false'},
            {'name': 'remarque', 'label': 'Remarque', 'field_type': FieldType.TEXTAREA, 'is_required': False, 'placeholder': 'Remarques supplémentaires...'},
        ]

        for order, field_data in enumerate(fields_data, start=1):
            FormField.objects.create(
                form=form,
                order=order,
                **field_data
            )

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} form "{form.title}" with {len(fields_data)} fields.'))
