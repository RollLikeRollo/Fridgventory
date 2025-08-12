from django.core.management.base import BaseCommand
from django.core.management import call_command
import subprocess
import sys
from pathlib import Path


class Command(BaseCommand):
    help = 'Update translations and help manage localization'

    def add_arguments(self, parser):
        parser.add_argument(
            '--language',
            type=str,
            help='Language code to update (e.g., cs, de, fr)',
        )
        parser.add_argument(
            '--add-language',
            type=str,
            help='Add a new language (e.g., de, fr, es)',
        )
        parser.add_argument(
            '--compile',
            action='store_true',
            help='Compile message files after updating',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show translation statistics',
        )

    def handle(self, *args, **options):
        if options['add_language']:
            self.add_new_language(options['add_language'])
        elif options['stats']:
            self.show_translation_stats()
        else:
            self.update_existing_translations(options.get('language'))
            
        if options['compile']:
            self.compile_messages()

    def add_new_language(self, lang_code):
        """Add a new language to the project."""
        self.stdout.write(f'Adding new language: {lang_code}')
        
        # Create message files for the new language
        call_command('makemessages', '-l', lang_code)
        
        # Update settings.py to include the new language
        settings_path = Path('core/settings.py')
        if settings_path.exists():
            content = settings_path.read_text()
            
            # Find the LANGUAGES setting
            if 'LANGUAGES = [' in content:
                # Add the new language (you'll need to update the language name manually)
                self.stdout.write(
                    self.style.WARNING(
                        f'Please add ({lang_code}, "Language Name") to the LANGUAGES setting in core/settings.py'
                    )
                )
            
        self.stdout.write(
            self.style.SUCCESS(f'Language {lang_code} added successfully!')
        )
        self.stdout.write('Next steps:')
        self.stdout.write('1. Add the language to LANGUAGES in core/settings.py')
        self.stdout.write(f'2. Translate strings in locale/{lang_code}/LC_MESSAGES/django.po')
        self.stdout.write('3. Run: python manage.py update_translations --compile')

    def update_existing_translations(self, language=None):
        """Update translation files."""
        if language:
            self.stdout.write(f'Updating translations for: {language}')
            call_command('makemessages', '-l', language)
        else:
            self.stdout.write('Updating all translations...')
            call_command('makemessages', '-l', 'en', '-l', 'cs')

    def compile_messages(self):
        """Compile message files."""
        self.stdout.write('Compiling message files...')
        call_command('compilemessages')
        self.stdout.write(self.style.SUCCESS('Messages compiled successfully!'))

    def show_translation_stats(self):
        """Show translation statistics for all languages."""
        locale_path = Path('locale')
        
        if not locale_path.exists():
            self.stdout.write(self.style.ERROR('No locale directory found'))
            return
            
        self.stdout.write('Translation Statistics:')
        self.stdout.write('=' * 50)
        
        for lang_dir in locale_path.iterdir():
            if lang_dir.is_dir():
                po_file = lang_dir / 'LC_MESSAGES' / 'django.po'
                if po_file.exists():
                    self.show_language_stats(lang_dir.name, po_file)

    def show_language_stats(self, lang_code, po_file):
        """Show statistics for a specific language."""
        try:
            content = po_file.read_text(encoding='utf-8')
            
            # Count total msgid entries (excluding the header)
            total_strings = content.count('msgid "') - 1  # Subtract header
            
            # Count empty translations
            empty_translations = content.count('msgstr ""')
            
            # Count fuzzy translations
            fuzzy_count = content.count('#, fuzzy')
            
            translated = total_strings - empty_translations - fuzzy_count
            percentage = (translated / total_strings * 100) if total_strings > 0 else 0
            
            self.stdout.write(f'{lang_code.upper()}: {translated}/{total_strings} strings translated ({percentage:.1f}%)')
            if fuzzy_count > 0:
                self.stdout.write(f'  - {fuzzy_count} fuzzy translations need review')
            if empty_translations > 0:
                self.stdout.write(f'  - {empty_translations} missing translations')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading {po_file}: {e}'))
