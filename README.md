# 🧊 Fridgventory

> **A modern, self-hosted kitchen inventory management system that actually makes sense.**

Fridgventory helps you track what you have, what you need, and where everything is stored in your kitchen. Never run out of essentials again, and say goodbye to buying duplicates of items you already have hidden in the back of your pantry.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com/r/rolllikerollo/fridgventory)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2+-092e20?logo=django)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## AI USE DISCLAIMER

Yes, this project's foundations were mostly created by the help of generative AI (Cursor, Claude-4-sonnet). I am aware that many people in the community do not like it, but it enables me, a junior developer, to create a valueable project for myself after my work duties, in my free time with ease. The project would not exist if I were to write every line of code myself from scratch.  

All contributions are welcome - human, AI, or combination of both.

Thanks for understanding,  
Jan, the main lead.

## ✨ Why Fridgventory?

- **🎯 Purpose-Built**: Designed specifically for kitchen inventory, not adapted from generic tools
- **📱 Modern Interface**: Responsive design that works on phones, tablets, and computers
- **⚡ Lightning Fast**: Inline editing, quantity adjustment buttons, and real-time updates
- **🏷️ Smart Organization**: Visual tags and locations with automatic color/emoji assignment
- **📝 Shopping Lists**: Generate formatted shopping lists as text or images
- **🌍 Multi-Language**: Built-in internationalization (English/Czech, easily extensible)
- **🐳 Easy Deployment**: One-command Docker setup or traditional Python installation
- **🔧 Extensible**: Plugin system for custom functionality

## 🚀 Key Features

### 📊 **Smart Inventory Tracking**
- Track desired vs. current quantities for any item
- Automatic "missing quantity" calculations
- Inline editing with double-click to modify any field
- One-click quantity adjustment buttons (➕/➖)

### 🏷️ **Visual Organization**
- **Tags**: Categorize items (dairy, vegetables, snacks, etc.)
- **Locations**: Track where items are stored (fridge, pantry, freezer, etc.)
- **Auto-styling**: Intelligent color and emoji assignment based on names
- **Custom styling**: Override colors and emojis for any tag or location
- **Emoji picker**: Beautiful, categorized emoji selection interface

### 📋 **Shopping Lists**
- **Text format**: Clean, printable shopping lists
- **Image format**: Visual shopping lists perfect for mobile screenshots
- **Auto-generation**: Only includes items you're actually missing

### ⚡ **Modern UX**
- **Responsive design**: Works on any device size
- **Dark/Light themes**: Respects your system preferences
- **Instant updates**: No page reloads for common actions
- **Smart search**: Find items by name, tag, or location
- **Sortable tables**: Click any column header to sort

### 🛠️ **Developer Friendly**
- **Plugin system**: Extend functionality with custom plugins
- **Clean codebase**: Well-documented Django application
- **Easy theming**: CSS custom properties for easy customization
- **REST-like APIs**: JSON endpoints for modern interactions

## 🏃‍♂️ Quick Start

### 🐳 Docker (Recommended)

**Requirements**: Docker and Docker Compose

```bash
# Clone and start
git clone https://github.com/your-username/fridgventory.git
cd fridgventory
docker-compose up -d

# Visit http://localhost:8000
```

That's it! 🎉

<details>
<summary>🔧 Additional Docker commands</summary>

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Create admin user (optional)
docker-compose exec web python manage.py createsuperuser

# Update to latest version
docker-compose pull
docker-compose up -d
```
</details>

### 🐍 Manual Installation

**Requirements**: Python 3.11+

```bash
# Setup environment
git clone https://github.com/your-username/fridgventory.git
cd fridgventory
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install and run
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Visit http://localhost:8000
```

## 📖 How to Use

### 1. **Add Your First Items**
- Click "Add Item" and enter details
- Set desired vs. current quantities
- Add tags like "dairy", "vegetables", "frozen"
- Specify locations like "fridge", "pantry", "freezer"

### 2. **Manage Your Inventory**
- **Quick updates**: Use ➕/➖ buttons to adjust quantities
- **Detailed editing**: Double-click any field to edit in-place
- **Visual organization**: Items are automatically color-coded by tags/locations

### 3. **Generate Shopping Lists**
- Missing items (where current < desired) automatically appear
- Download as text file or image
- Perfect for grocery shopping or meal planning

### 4. **Customize Your Setup**
- Visit Settings to manage tags and locations
- Override default colors and emojis
- Set up your preferred organization system

## 🎯 Perfect For

- **🏠 Home cooks** who want to stay organized
- **👨‍👩‍👧‍👦 Families** managing multiple food preferences  
- **🍽️ Meal planners** who prep in advance
- **🏪 Small food businesses** tracking inventory
- **🚐 RV/Boat owners** with limited storage space
- **🏠 Anyone** tired of overbuying or running out of essentials

## 🔧 Configuration

### Environment Variables

```bash
# Language (default: en)
DEFAULT_LANGUAGE=en  # or 'cs' for Czech

# Django settings
DEBUG=1              # Set to 0 in production
SECRET_KEY=your-secret-key
```

### Custom Plugins

Create plugins in the `plugins/` directory:

```python
# plugins/my_plugin/plugin.py
def on_ready():
    """Called when the application starts"""
    print("My plugin is ready!")
```

## 🌍 Internationalization

Fridgventory supports multiple languages:

- **🇺🇸 English** (default)
- **🇨🇿 Czech** (česky)
- **➕ More languages**: Easy to add via Django's i18n system

Want to add your language? See our [translation guide](docs/TRANSLATIONS.md)!

## 🤝 Contributing

We'd love your help making Fridgventory even better! 

### Planned
- Integration with barcode scanner app called BarcodeBuddy -  [BarcodeBuddy project](https://github.com/Forceu/barcodebuddy)

### 🐛 Found a Bug?
- Check [existing issues](../../issues)
- Create a [new issue](../../issues/new) with details

### 💡 Have an Idea?
- Start a [discussion](../../discussions) 
- Submit a feature request

### 👨‍💻 Want to Code?
1. Fork the repository
2. Create a feature branch (`git checkout -b amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### 🌍 Translation Help
We need translators! See [TRANSLATIONS.md](docs/TRANSLATIONS.md) for details.

## 🏗️ Technology Stack

- **Backend**: Django 5.2+ (Python)
- **Frontend**: Vanilla JavaScript, modern CSS
- **Database**: SQLite (default), PostgreSQL/MySQL supported
- **Styling**: CSS custom properties, responsive design
- **Deployment**: Docker, traditional Python hosting
- **Internationalization**: Django i18n framework

## 📸 Screenshots

*Coming soon! We're working on adding screenshots to showcase the interface.*

## 🗺️ Roadmap

- [ ] 📱 Progressive Web App (PWA) support
- [ ] 📊 Usage analytics and insights
- [ ] 📅 Expiration date tracking
- [ ] 🔄 Automatic inventory suggestions
- [ ] 📱 Mobile app (React Native)
- [ ] 🛒 Grocery store integration APIs
- [ ] 📈 Nutrition information integration

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with ❤️ using [Django](https://www.djangoproject.com/)
- Emoji picker inspired by modern web interfaces
- Icons and emojis from the Unicode standard
- Community feedback and testing

---

**Ready to take control of your kitchen inventory?** 

[⭐ Star this repo](../../stargazers) | [🐳 Pull from DockerHub](https://hub.docker.com/r/rolllikerollo/fridgventory) | [💬 Join the discussion](../../discussions)
