from django.core.management.base import BaseCommand
from academic.models import Etablissement, Faculte, Domaine, Specialite


class Command(BaseCommand):
    help = 'Seed academic data (Etablissements, Facultes, Domaines, Specialites)'

    def handle(self, *args, **options):
        # Create Etablissement
        ufas, _ = Etablissement.objects.get_or_create(
            nom="Université Ferhat Abbas Sétif 1",
            defaults={'adresse': 'Campus El Bez, Sétif 19000, Algérie'}
        )
        
        # Create Facultes
        facultes_data = [
            "Faculté des Sciences",
            "Faculté de Technologie",
            "Faculté des Sciences de la Nature et de la Vie",
            "Faculté de Médecine",
            "Faculté d'Architecture",
            "Faculté des Sciences Économiques, Commerciales et des Sciences de Gestion",
        ]
        
        facultes = {}
        for nom in facultes_data:
            fac, _ = Faculte.objects.get_or_create(nom=nom, etablissement=ufas)
            facultes[nom] = fac
        
        # Create Domaines and Specialites
        domaines_specialites = {
            "Faculté des Sciences": {
                "Mathématiques et Informatique": [
                    "Informatique",
                    "Mathématiques",
                    "Recherche Opérationnelle",
                    "Intelligence Artificielle",
                    "Systèmes d'Information",
                ],
                "Sciences de la Matière": [
                    "Physique",
                    "Chimie",
                    "Physique des Matériaux",
                ],
            },
            "Faculté de Technologie": {
                "Sciences et Technologies": [
                    "Génie Civil",
                    "Génie Mécanique",
                    "Génie Électrique",
                    "Électronique",
                    "Automatique",
                    "Télécommunications",
                ],
                "Génie des Procédés": [
                    "Génie Chimique",
                    "Génie des Matériaux",
                ],
            },
            "Faculté des Sciences de la Nature et de la Vie": {
                "Sciences Biologiques": [
                    "Biochimie",
                    "Microbiologie",
                    "Biologie Moléculaire",
                    "Écologie",
                ],
                "Sciences Agronomiques": [
                    "Agronomie",
                    "Sciences Alimentaires",
                ],
            },
            "Faculté de Médecine": {
                "Sciences Médicales": [
                    "Médecine Générale",
                    "Pharmacie",
                    "Chirurgie Dentaire",
                ],
            },
            "Faculté d'Architecture": {
                "Architecture et Urbanisme": [
                    "Architecture",
                    "Urbanisme",
                ],
            },
            "Faculté des Sciences Économiques, Commerciales et des Sciences de Gestion": {
                "Sciences Économiques": [
                    "Économie",
                    "Finance",
                    "Comptabilité",
                ],
                "Sciences de Gestion": [
                    "Management",
                    "Marketing",
                    "Gestion des Ressources Humaines",
                ],
                "Sciences Commerciales": [
                    "Commerce International",
                ],
            },
        }
        
        domaine_count = 0
        specialite_count = 0
        
        for fac_nom, domaines in domaines_specialites.items():
            faculte = facultes.get(fac_nom)
            if not faculte:
                continue
                
            for domaine_nom, specialites in domaines.items():
                domaine, created = Domaine.objects.get_or_create(
                    nom=domaine_nom,
                    faculte=faculte
                )
                if created:
                    domaine_count += 1
                
                for spec_nom in specialites:
                    _, created = Specialite.objects.get_or_create(
                        nom=spec_nom,
                        domaine=domaine
                    )
                    if created:
                        specialite_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f'Seeded: 1 Etablissement, {len(facultes)} Facultes, {domaine_count} Domaines, {specialite_count} Specialites'
        ))
