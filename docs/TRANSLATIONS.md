# 🌍 Translation Guide for Fridgventory

This guide explains how to work with translations in Fridgventory and how to add new languages.

## 📋 Current Status

- **English**: Source language (complete)
- **Czech**: 72/308 strings translated (23.4%)

## 🛠️ Management Commands

### Check Translation Statistics
```bash
python manage.py update_translations --stats
```

### Update Existing Translations
```bash
# Update all languages
python manage.py update_translations

# Update specific language
python manage.py update_translations --language cs

# Update and compile
python manage.py update_translations --compile
```

### Add New Language
```bash
python manage.py update_translations --add-language de
```

## 🌟 Adding a New Language

### Step 1: Generate Translation Files
```bash
python manage.py update_translations --add-language [LANGUAGE_CODE]
```
Example: `python manage.py update_translations --add-language de`

### Step 2: Update Settings
Add the new language to `core/settings.py`:
```python
LANGUAGES = [
    ('en', 'English'),
    ('cs', 'Čeština'),
    ('de', 'Deutsch'),  # Add your new language here
]
```

### Step 3: Translate Strings
Edit the file `locale/[LANGUAGE_CODE]/LC_MESSAGES/django.po` and translate the strings:
```po
msgid "Items"
msgstr "Artikel"  # German translation
```

### Step 4: Compile Translations
```bash
python manage.py update_translations --compile
```

### Step 5: Test
Navigate to your site and use the language toggle to test the new language.

## 📝 Translation File Structure

Translation files are located in:
```
locale/
├── en/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
├── cs/
│   └── LC_MESSAGES/
│       ├── django.po
│       └── django.mo
└── [new_language]/
    └── LC_MESSAGES/
        ├── django.po
        └── django.mo
```

## 🎯 Key Areas to Translate

### Core UI Elements
- Navigation items (Home, Add Item, Settings)
- Buttons (Save, Cancel, Edit, Delete)
- Form labels and placeholders
- Table headers

### Feature-Specific Terms
- **Search**: "Search items, tags, or locations..."
- **Tags**: Tag names and management interface
- **Locations**: Location names and management interface
- **Shopping Lists**: Export formats and messages

### Messages and Notifications
- Success/error messages
- Confirmation dialogs
- Empty state messages

## 🔧 Developer Guidelines

### Marking Strings for Translation
Use Django's translation functions:

```python
from django.utils.translation import gettext as _

# In views
message = _("Item saved successfully!")

# In templates
{% load i18n %}
{% trans "Define New Item" %}

# With variables
{% blocktrans with name=item.name %}
Delete item "{{ name }}"?
{% endblocktrans %}
```

### Best Practices
1. **Keep strings short and context-clear**
2. **Use descriptive msgid values**
3. **Include context when the same English word has different meanings**
4. **Test translations in context, not just isolated strings**

## 🚀 Automated Translation Workflow

### For Contributors
1. **Clone the repository**
2. **Add your language** using the management command
3. **Translate strings** in the .po file
4. **Test locally** by compiling and running the server
5. **Submit a Pull Request** with your translations

### For Maintainers
1. **Review translation quality**
2. **Test language switching**
3. **Check for missing translations**
4. **Merge and deploy**

## 🌐 Language Codes Reference

Common language codes:
- `de` - German (Deutsch)
- `fr` - French (Français)
- `es` - Spanish (Español)
- `it` - Italian (Italiano)
- `pl` - Polish (Polski)
- `ru` - Russian (Русский)
- `zh` - Chinese (中文)
- `ja` - Japanese (日本語)
- `ko` - Korean (한국어)

## 🔍 Testing Translations

### Manual Testing
1. **Compile translations**: `python manage.py compilemessages`
2. **Run server**: `python manage.py runserver`
3. **Switch languages** using the language toggle
4. **Navigate all pages** to verify translations
5. **Test with different data** (long item names, many tags, etc.)

### Automated Testing
```bash
# Check for missing translations
python manage.py update_translations --stats

# Validate translation files
python manage.py compilemessages --verbosity=2
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Translations not appearing
- **Check if messages are compiled**: `python manage.py compilemessages`
- **Verify LOCALE_PATHS in settings.py**
- **Clear browser cache**

#### 2. Language toggle not working
- **Check if language is in LANGUAGES setting**
- **Verify i18n URLs are configured**
- **Check middleware order** (LocaleMiddleware should be early)

#### 3. Incomplete translations
- **Use `--stats` to check completion**
- **Look for fuzzy translations** (marked with `#, fuzzy`)
- **Run makemessages** to capture new strings

### Debugging Commands
```bash
# Verbose compilation to see errors
python manage.py compilemessages --verbosity=2

# Force update of translation files
python manage.py makemessages --all --ignore=venv

# Check Django's language detection
python manage.py shell -c "from django.utils import translation; print(translation.get_language())"
```

## 🤝 Contributing Translations

We welcome contributions! Here's how to help:

1. **Check current status** with `--stats`
2. **Pick a language** you're fluent in
3. **Translate systematically** (UI first, then messages)
4. **Test thoroughly** in different browsers
5. **Submit a Pull Request** with:
   - Updated .po files
   - Updated LANGUAGES in settings.py
   - Testing notes

### Quality Guidelines
- **Use native-level fluency** only
- **Maintain consistent terminology** within the application
- **Consider cultural context** (date formats, currency, etc.)
- **Keep technical terms** in their commonly used form
- **Test with real data** to ensure UI layout works

## 📞 Support

For translation-related questions:
1. **Check this documentation** first
2. **Use the `update_translations` management command** for common tasks
3. **Open an issue** for bugs or unclear documentation
4. **Join discussions** in Pull Requests for translation improvements

---

## 🎉 Thank You!

Every translation makes Fridgventory accessible to more users worldwide. Your contributions matter! 🌍
