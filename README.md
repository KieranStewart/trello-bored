# Trello Bored

## Created by

[![gabrielhwilliams](https://img.shields.io/badge/gabrielhwilliams-000?style=for-the-badge&logo=github)](https://github.com/gabrielhwilliams)
[![Aj-fior60](https://img.shields.io/badge/Aj--fior60-000?style=for-the-badge&logo=github)](https://github.com/Aj-fior60)
[![KieranStewart](https://img.shields.io/badge/KieranStewart-000?style=for-the-badge&logo=github)](https://github.com/KieranStewart)
[![atauln](https://img.shields.io/badge/atauln-000?style=for-the-badge&logo=github)](https://github.com/atauln)
[![AJBruno23](https://img.shields.io/badge/AJBruno23-000?style=for-the-badge&logo=github)](https://github.com/AJBruno23)
[![OwenCHowell](https://img.shields.io/badge/OwenCHowell-000?style=for-the-badge&logo=github)](https://github.com/OwenCHowell)


## Project Mission

The original project mission statement was as follows: Create a workflow management system that updates project story cards based on commits to a repository. This was derived from the original idea, which had two requirements.
* Automatic Trello/Jira management that tracks commits and automatically checks off user stories and implementation requirements
* Links with project management workflows and suggests updates to workflows and tasks

After working on and completing the MVP for the project, these are the core features and functionality of the product:
* Link Git workflow events to project management cards
* Automatically move tickets between In Progress, In Review, and Done
* AI‑powered ticket association based on commit messages, PR diffs, and branch names
* VS Code extension for approving or denying suggested updates
* GitHub Actions pipeline to detect PR creation, merge, review, and branch creation
* Backend API to coordinate automation, AI, and board updates

## How It Works [![Static Badge](https://img.shields.io/badge/Demo-grey?style=for-the-badge&logo=googledrive&logoColor=%234183C4&logoSize=auto)](https://drive.google.com/file/d/1TMBCiqAb0dGF2uVHmui9aMh8_HPzOwok/view?usp=sharing)

The system is comprised of 4 seperate parts that work together as a whole to allow the automation of the projects board. A short demo of their functionality can be found above.

### 1. GitHub Actions

The system listens for:

* Branch creation
* PR creation
* PR review
* PR merge

Each event triggers an API call to the backend with commit data, diffs, and metadata.

### 2. Backend API (Flask)

The backend:

* Parses incoming GitHub event data
* Calls Gemini AI to identify relevant tickets
* Updates GitHub Projects via the proxy interface
* Notifies connected VS Code clients of pending changes

### 3. AI Ticket Association

Gemini analyzes:

* Commit messages
* PR diffs
* Branch names
* Code context

It returns a list of tickets likely associated with the change.

### 4. VS Code Extension

Developers can:

* Approve or deny suggested ticket updates
* View To‑Do items
* View historical (Done) tickets
* Manage session settings

All interactions occur directly inside VS Code.

## System Architecture

```
trello-bored
├── .github/workflows        # GitHub Actions for workflow automation
├── bored-api/               # Backend API (Flask)
│   ├── proxy-mgmt/          # Project board proxy interface + GitHub Projects implementation
│   ├── ai.py                # Gemini AI integration
│   ├── bored_api.py         # REST API endpoints
│   ├── client.py            # Session management
│   ├── tools.py             # Utility functions
│   └── update.py            # Deployment pipeline
└── vs-code/trelloboredextension
    ├── src/                 # VS Code extension logic
    │   ├── views/           # HTML views (approve, todo, historical)
    │   ├── script/          # JS logic for UI interactions
    │   ├── style/           # CSS styling
    │   ├── extension.ts     # Extension entry point
    │   └── SidebarProvider.ts
    └── README.md            # Extension setup instructions
```
