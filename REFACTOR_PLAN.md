# Code Refactoring Plan

## Current Issues with main.py
- Over 400 lines of code
- Multiple responsibilities mixed together
- Hard to maintain and debug
- Difficult to test individual components

## Recommended File Structure

```
mail-agent/
├── main.py                 # Main Streamlit app entry point (50-75 lines)
├── config.py              # Configuration and constants
├── components/
│   ├── __init__.py
│   ├── agentmail_utils.py  # Already exists - AgentMail API functions
│   ├── ai_utils.py         # Already exists - AI generation functions
│   ├── ui_components.py    # Reusable UI components
│   └── email_manager.py    # Email handling logic
├── pages/
│   ├── __init__.py
│   ├── email_composer.py   # Email composition UI
│   ├── inbox_manager.py    # Inbox selection and management
│   └── email_sender.py     # Email sending and approval workflow
└── utils/
    ├── __init__.py
    ├── session_manager.py  # Session state management
    └── validators.py       # Email validation and helpers
```

## Benefits of Refactoring
1. **Maintainability**: Easier to find and fix bugs
2. **Scalability**: Easy to add new features
3. **Testability**: Can test individual components
4. **Collaboration**: Multiple developers can work on different parts
5. **Reusability**: Components can be reused across different parts

## Migration Strategy
1. Start by extracting UI components
2. Move session state management to separate file
3. Create dedicated email workflow management
4. Keep main.py as thin coordinator

## Priority
**HIGH** - The current code is already becoming unwieldy. Refactoring now will save significant time in the future.
