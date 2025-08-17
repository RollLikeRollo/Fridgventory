// Autocomplete functionality for the item form

let autocompleteData = {
    tags: [],
    locations: []
};

let currentInput = null;
let currentDropdown = null;
let highlightedIndex = -1;

// Initialize autocomplete functionality
function initializeAutocomplete() {
    const tagsInput = document.getElementById('tags-input');
    const locationsInput = document.getElementById('locations-input');
    
    if (tagsInput) {
        setupAutocomplete(tagsInput, 'tags');
    }
    
    if (locationsInput) {
        setupAutocomplete(locationsInput, 'locations');
    }
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.autocomplete-container')) {
            hideDropdown();
        }
    });
}

// Setup autocomplete for a specific input
function setupAutocomplete(input, type) {
    const dropdown = document.getElementById(type + '-dropdown');
    
    input.addEventListener('input', function(e) {
        handleInputChange(input, dropdown, type);
    });
    
    input.addEventListener('keydown', function(e) {
        handleKeyDown(e, input, dropdown, type);
    });
    
    input.addEventListener('focus', function(e) {
        if (input.value.trim()) {
            handleInputChange(input, dropdown, type);
        }
    });
}

// Handle input changes and fetch suggestions
function handleInputChange(input, dropdown, type) {
    const value = input.value.trim();
    const cursorPosition = input.selectionStart;
    
    // Get the current word being typed (for comma-separated values)
    const beforeCursor = value.substring(0, cursorPosition);
    const afterCursor = value.substring(cursorPosition);
    
    const lastCommaIndex = beforeCursor.lastIndexOf(',');
    const nextCommaIndex = afterCursor.indexOf(',');
    
    let currentWord;
    if (lastCommaIndex === -1) {
        // No comma before cursor, word starts from beginning
        currentWord = nextCommaIndex === -1 ? beforeCursor : beforeCursor + afterCursor.substring(0, nextCommaIndex);
    } else {
        // Word starts after the last comma
        const wordStart = beforeCursor.substring(lastCommaIndex + 1).trim();
        currentWord = nextCommaIndex === -1 ? wordStart : wordStart + afterCursor.substring(0, nextCommaIndex);
    }
    
    currentWord = currentWord.trim();
    
    if (currentWord.length < 1) {
        hideDropdown();
        return;
    }
    
    currentInput = input;
    currentDropdown = dropdown;
    highlightedIndex = -1;
    
    // Fetch suggestions
    fetchSuggestions(currentWord, type).then(suggestions => {
        showDropdown(dropdown, suggestions, currentWord, type);
    });
}

// Fetch suggestions from the API
async function fetchSuggestions(query, type) {
    try {
        const url = `/api/autocomplete/${type}/?q=${encodeURIComponent(query)}`;
        const response = await fetch(url);
        const data = await response.json();
        
        let suggestions = data.results || [];
        
        // Add "Create new" option if query doesn't match exactly
        const exactMatch = suggestions.find(s => s.name.toLowerCase() === query.toLowerCase());
        if (!exactMatch && query.trim()) {
            suggestions.push({
                name: query,
                emoji: type === 'tags' ? '🏷️' : '📍',
                color: '#6b7280',
                type: 'new'
            });
        }
        
        return suggestions;
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        return [];
    }
}

// Show the dropdown with suggestions
function showDropdown(dropdown, suggestions, query, type) {
    dropdown.innerHTML = '';
    
    if (suggestions.length === 0) {
        hideDropdown();
        return;
    }
    
    suggestions.forEach((suggestion, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        
        if (suggestion.type === 'new') {
            item.classList.add('create-new');
        }
        
        item.innerHTML = `
            <span class="autocomplete-emoji">${suggestion.emoji}</span>
            <span class="autocomplete-name">${suggestion.name}</span>
            ${suggestion.type === 'new' ? '<span class="create-new-icon">(Create new ✨)</span>' : ''}
        `;
        
        item.addEventListener('click', function() {
            selectSuggestion(suggestion);
        });
        
        item.addEventListener('mouseenter', function() {
            highlightedIndex = index;
            updateHighlight();
        });
        
        dropdown.appendChild(item);
    });
    
    dropdown.classList.add('active');
    updateHighlight();
}

// Hide the dropdown
function hideDropdown() {
    if (currentDropdown) {
        currentDropdown.classList.remove('active');
        currentDropdown.innerHTML = '';
    }
    currentInput = null;
    currentDropdown = null;
    highlightedIndex = -1;
}

// Handle keyboard navigation
function handleKeyDown(e, input, dropdown, type) {
    if (!dropdown.classList.contains('active')) {
        return;
    }
    
    const items = dropdown.querySelectorAll('.autocomplete-item');
    
    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            highlightedIndex = Math.min(highlightedIndex + 1, items.length - 1);
            updateHighlight();
            break;
            
        case 'ArrowUp':
            e.preventDefault();
            highlightedIndex = Math.max(highlightedIndex - 1, -1);
            updateHighlight();
            break;
            
        case 'Enter':
            e.preventDefault();
            if (highlightedIndex >= 0 && items[highlightedIndex]) {
                const suggestion = extractSuggestionFromElement(items[highlightedIndex]);
                selectSuggestion(suggestion);
            }
            break;
            
        case 'Escape':
            hideDropdown();
            break;
    }
}

// Update highlighted item in dropdown
function updateHighlight() {
    if (!currentDropdown) return;
    
    const items = currentDropdown.querySelectorAll('.autocomplete-item');
    items.forEach((item, index) => {
        item.classList.toggle('highlighted', index === highlightedIndex);
    });
}

// Extract suggestion data from DOM element
function extractSuggestionFromElement(element) {
    const name = element.querySelector('.autocomplete-name').textContent;
    const emoji = element.querySelector('.autocomplete-emoji').textContent;
    const isNew = element.classList.contains('create-new');
    
    return {
        name: name,
        emoji: emoji,
        type: isNew ? 'new' : 'existing'
    };
}

// Select a suggestion and update the input
function selectSuggestion(suggestion) {
    if (!currentInput) return;
    
    const value = currentInput.value;
    const cursorPosition = currentInput.selectionStart;
    
    // Find the word boundaries
    const beforeCursor = value.substring(0, cursorPosition);
    const afterCursor = value.substring(cursorPosition);
    
    const lastCommaIndex = beforeCursor.lastIndexOf(',');
    const nextCommaIndex = afterCursor.indexOf(',');
    
    let newValue;
    let newCursorPosition;
    
    if (lastCommaIndex === -1) {
        // No comma before, replace from beginning
        const afterWord = nextCommaIndex === -1 ? '' : afterCursor.substring(nextCommaIndex);
        newValue = suggestion.name + afterWord;
        newCursorPosition = suggestion.name.length;
    } else {
        // Replace the word after the last comma
        const beforeWord = beforeCursor.substring(0, lastCommaIndex + 1) + ' ';
        const afterWord = nextCommaIndex === -1 ? '' : afterCursor.substring(nextCommaIndex);
        newValue = beforeWord + suggestion.name + afterWord;
        newCursorPosition = beforeWord.length + suggestion.name.length;
    }
    
    currentInput.value = newValue;
    currentInput.setSelectionRange(newCursorPosition, newCursorPosition);
    
    // Show notification for new items
    if (suggestion.type === 'new') {
        showNewItemNotification(suggestion.name, currentInput.name);
    }
    
    hideDropdown();
    currentInput.focus();
}

// Initialize clickable suggestions
function initializeClickableSuggestions() {
    const suggestions = document.querySelectorAll('.clickable-suggestion');
    
    suggestions.forEach(suggestion => {
        suggestion.addEventListener('click', function() {
            const value = this.getAttribute('data-value');
            const targetId = this.getAttribute('data-target');
            const targetInput = document.getElementById(targetId);
            
            if (targetInput && value) {
                addToCommaList(targetInput, value);
                targetInput.focus();
            }
        });
    });
}

// Add value to comma-separated list in input
function addToCommaList(input, value) {
    const currentValue = input.value.trim();
    
    // Check if value already exists
    const values = currentValue.split(',').map(v => v.trim()).filter(v => v);
    if (values.includes(value)) {
        return; // Already exists
    }
    
    // Add the new value
    if (currentValue) {
        input.value = currentValue + ', ' + value;
    } else {
        input.value = value;
    }
}

// Show notification for new items
function showNewItemNotification(itemName, fieldType) {
    const notification = document.getElementById('form-notifications');
    const message = document.getElementById('notification-message');
    const list = document.getElementById('new-items-list');
    
    if (!notification || !message || !list) return;
    
    const typeLabel = fieldType === 'tags' ? 'tag' : 'location';
    
    // Get existing new items from the list
    const existingItems = Array.from(list.children).map(li => li.textContent);
    const newItemText = `New ${typeLabel}: ${itemName}`;
    
    // Add if not already in the list
    if (!existingItems.includes(newItemText)) {
        const li = document.createElement('li');
        li.textContent = newItemText;
        list.appendChild(li);
    }
    
    // Update message
    const itemCount = list.children.length;
    message.textContent = `The following ${itemCount === 1 ? 'item' : 'items'} will be created when you save:`;
    
    // Show notification
    notification.style.display = 'block';
}

// Form validation
function initializeFormValidation() {
    const form = document.getElementById('item-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            const nameInput = document.getElementById('item-name');
            
            if (nameInput && !nameInput.value.trim()) {
                e.preventDefault();
                nameInput.focus();
                alert('Please enter an item name.');
                return false;
            }
        });
    }
}
