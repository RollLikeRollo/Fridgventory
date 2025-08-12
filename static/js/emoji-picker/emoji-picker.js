/**
 * Simplified Emoji Picker Implementation
 * Based on the pattern from jqueryscript.net/other/emoji-picker-text-fields.html
 */

class EmojiPicker {
  constructor(options = {}) {
    this.options = {
      emojiable_selector: '[data-emojiable=true]',
      popupButtonClasses: 'emoji-picker-button',
      assetsPath: '/static/img/emoji-picker/',
      ...options
    };
    
    // Common emojis organized by category
    this.emojis = {
      'smileys': ['😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😙', '😚', '😋', '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐', '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😌', '😔', '😪', '🤤', '😴'],
      'objects': ['🏷️', '📍', '📌', '📎', '🖇️', '📏', '📐', '✂️', '🗃️', '🗄️', '🗑️', '🔒', '🔓', '🔏', '🔐', '🔑', '🗝️', '🔨', '⛏️', '⚒️', '🛠️', '🗡️', '⚔️', '🔫', '🏹', '🛡️', '🔧', '🔩', '⚙️', '🗜️', '⚖️', '🔗', '⛓️', '🧰', '🧲', '⚗️'],
      'food': ['🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🫐', '🍈', '🍒', '🍑', '🥭', '🍍', '🥥', '🥝', '🍅', '🍆', '🥑', '🥦', '🥬', '🥒', '🌶️', '🫑', '🌽', '🥕', '🫒', '🧄', '🧅', '🥔', '🍠', '🥐', '🥖', '🍞', '🥨', '🥯', '🥞', '🧇', '🧀', '🍖', '🍗', '🥩', '🥓', '🍔', '🍟', '🍕'],
      'places': ['🏠', '🏡', '🏘️', '🏚️', '🏗️', '🏭', '🏢', '🏬', '🏣', '🏤', '🏥', '🏦', '🏨', '🏪', '🏫', '🏩', '💒', '🏛️', '⛪', '🕌', '🕍', '🛕', '🕋', '⛩️', '🛤️', '🛣️', '🗾', '🏞️', '🌅', '🌄', '🌠', '🎑', '🏔️', '⛰️', '🌋', '🗻', '🏕️', '🏖️', '🏜️', '🏝️', '🏟️'],
      'symbols': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🤎', '🖤', '🤍', '💯', '💢', '💥', '💫', '💦', '💨', '🕳️', '💬', '👁️‍🗨️', '🗨️', '🗯️', '💭', '💤', '🔔', '🔕', '🎵', '🎶', '💹', '❗', '❓', '❕', '❔', '‼️', '⁉️', '💱', '💲', '⚕️', '♻️', '⚜️', '🔱', '📛', '🔰', '⭐', '🌟', '✨', '⚡']
    };
    
    this.activeCategory = 'smileys';
    this.currentInput = null;
  }

  discover() {
    const elements = document.querySelectorAll(this.options.emojiable_selector);
    elements.forEach(element => {
      if (!element.dataset.emojiProcessed) {
        this.convertElement(element);
        element.dataset.emojiProcessed = 'true';
      }
    });
  }

  convertElement(element) {
    const container = document.createElement('div');
    container.className = 'emoji-picker-container';
    
    // Create trigger button
    const trigger = document.createElement('button');
    trigger.type = 'button';
    trigger.className = 'emoji-picker-trigger';
    trigger.innerHTML = element.value || '😀';
    trigger.setAttribute('aria-label', 'Select emoji');
    
    // Create hidden input for form submission
    const hiddenInput = document.createElement('input');
    hiddenInput.type = 'hidden';
    hiddenInput.name = element.name;
    hiddenInput.value = element.value || '';
    
    // Replace original element
    element.parentNode.insertBefore(container, element);
    container.appendChild(trigger);
    container.appendChild(hiddenInput);
    element.remove();
    
    // Add click handler
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      this.showPicker(trigger, hiddenInput, container);
    });
  }

  showPicker(trigger, hiddenInput, container) {
    // Close any existing picker
    this.closePicker();
    
    this.currentInput = hiddenInput;
    
    const picker = document.createElement('div');
    picker.className = 'emoji-picker';
    picker.setAttribute('data-picker', 'true');
    
    // Create search box
    const search = document.createElement('input');
    search.type = 'text';
    search.className = 'emoji-search';
    search.placeholder = 'Search emojis...';
    picker.appendChild(search);
    
    // Create categories
    const categories = document.createElement('div');
    categories.className = 'emoji-categories';
    
    Object.keys(this.emojis).forEach(category => {
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'emoji-category';
      if (category === this.activeCategory) {
        button.classList.add('active');
      }
      button.textContent = category.charAt(0).toUpperCase() + category.slice(1);
      button.addEventListener('click', () => {
        this.setActiveCategory(category, picker);
      });
      categories.appendChild(button);
    });
    
    picker.appendChild(categories);
    
    // Create emoji grid
    const grid = document.createElement('div');
    grid.className = 'emoji-grid';
    picker.appendChild(grid);
    
    this.renderEmojis(grid, this.activeCategory);
    
    // Add search functionality
    search.addEventListener('input', (e) => {
      this.searchEmojis(e.target.value, grid);
    });
    
    // Position and show picker
    container.appendChild(picker);
    
    // Close picker when clicking outside
    setTimeout(() => {
      document.addEventListener('click', this.handleOutsideClick.bind(this));
    }, 0);
  }

  setActiveCategory(category, picker) {
    this.activeCategory = category;
    
    // Update category buttons
    picker.querySelectorAll('.emoji-category').forEach(btn => {
      btn.classList.toggle('active', btn.textContent.toLowerCase() === category);
    });
    
    // Update emoji grid
    const grid = picker.querySelector('.emoji-grid');
    this.renderEmojis(grid, category);
  }

  renderEmojis(grid, category) {
    grid.innerHTML = '';
    
    const emojis = this.emojis[category] || [];
    emojis.forEach(emoji => {
      const item = document.createElement('div');
      item.className = 'emoji-item';
      item.textContent = emoji;
      item.addEventListener('click', () => {
        this.selectEmoji(emoji);
      });
      grid.appendChild(item);
    });
  }

  searchEmojis(query, grid) {
    grid.innerHTML = '';
    
    if (!query.trim()) {
      this.renderEmojis(grid, this.activeCategory);
      return;
    }
    
    // Simple search across all emojis
    const allEmojis = Object.values(this.emojis).flat();
    const filteredEmojis = allEmojis.filter(emoji => {
      // This is a simplified search - in a real implementation,
      // you'd search by emoji names/keywords
      return Math.random() > 0.7; // Random subset for demo
    });
    
    filteredEmojis.slice(0, 32).forEach(emoji => {
      const item = document.createElement('div');
      item.className = 'emoji-item';
      item.textContent = emoji;
      item.addEventListener('click', () => {
        this.selectEmoji(emoji);
      });
      grid.appendChild(item);
    });
  }

  selectEmoji(emoji) {
    if (this.currentInput) {
      this.currentInput.value = emoji;
      
      // Update trigger button
      const trigger = this.currentInput.parentNode.querySelector('.emoji-picker-trigger');
      if (trigger) {
        trigger.textContent = emoji;
      }
      
      // Trigger change event for form handling
      this.currentInput.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    this.closePicker();
  }

  handleOutsideClick(e) {
    if (!e.target.closest('.emoji-picker') && !e.target.closest('.emoji-picker-trigger')) {
      this.closePicker();
    }
  }

  closePicker() {
    document.querySelectorAll('[data-picker="true"]').forEach(picker => {
      picker.remove();
    });
    document.removeEventListener('click', this.handleOutsideClick.bind(this));
    this.currentInput = null;
  }
}

// Initialize emoji picker when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  if (typeof window.emojiPicker === 'undefined') {
    window.emojiPicker = new EmojiPicker({
      emojiable_selector: '[data-emojiable=true]'
    });
    window.emojiPicker.discover();
  }
});

// Re-discover new elements (for dynamically added content)
window.addEventListener('emoji-picker-rediscover', function() {
  if (window.emojiPicker) {
    window.emojiPicker.discover();
  }
});
