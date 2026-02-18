import * as vscode from 'vscode';
import * as https from 'https';
import * as http from 'http';

export class SidebarProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    resolveWebviewView(webviewView: vscode.WebviewView) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlContent();

        webviewView.webview.onDidReceiveMessage(async message => {
            switch (message.command) {
                case 'fetchChanges':
                    await this._fetchAndDisplayChanges();
                    break;
                case 'saveSettings':
                    await this._saveSettings(message.serverUrl, message.boardUrl);
                    break;
                case 'loadSettings':
                    this._loadSettings();
                    break;
            }
        });
    }

    private async _saveSettings(serverUrl: string, boardUrl: string) {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        await config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Global);
        await config.update('boardUrl', boardUrl, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('Settings saved!');
    }

    private _loadSettings() {
        const config = vscode.workspace.getConfiguration('trelloboredextension');
        const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
        const boardUrl = config.get<string>('boardUrl', '');
        this._view?.webview.postMessage({ command: 'settingsLoaded', serverUrl, boardUrl });
    }

    private async _fetchAndDisplayChanges() {
        try {
            const config = vscode.workspace.getConfiguration('trelloboredextension');
            const serverUrl = config.get<string>('serverUrl', 'http://localhost:3000');
            const boardUrl = config.get<string>('boardUrl', '');
            const apiUrl = `${serverUrl}/api/changes${boardUrl ? '?board=' + boardUrl : ''}`;
            const data = await this._httpGet(apiUrl);
            this._view?.webview.postMessage({ command: 'updateChanges', data: JSON.parse(data) });
        } catch (error) {
            this._view?.webview.postMessage({ command: 'error', message: String(error) });
        }
    }

    private _httpGet(url: string): Promise<string> {
        return new Promise((resolve, reject) => {
            const client = url.startsWith('https') ? https : http;
            client.get(url, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => resolve(data));
            }).on('error', reject);
        });
    }

    private _getHtmlContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trello Bored</title>
    <style>
        body { padding: 10px; font-family: var(--vscode-font-family); }
        .settings { margin-bottom: 16px; padding: 12px; background: var(--vscode-editor-background); border-radius: 4px; }
        input { width: 100%; padding: 6px; margin: 4px 0 8px 0; background: var(--vscode-input-background); color: var(--vscode-input-foreground); border: 1px solid var(--vscode-input-border); }
        label { display: block; margin-top: 8px; font-size: 12px; }
        button { padding: 8px 16px; margin: 4px 4px 16px 0; cursor: pointer; }
        .change-item { padding: 8px; margin: 8px 0; border-left: 3px solid var(--vscode-button-background); background: var(--vscode-editor-background); }
        .error { color: var(--vscode-errorForeground); }
        .loading { color: var(--vscode-descriptionForeground); }
    </style>
</head>
<body>
    <h2>Trello Board Changes</h2>
    <div class="settings">
        <label>Server Base URL:</label>
        <input type="text" id="serverUrl" placeholder="http://localhost:3000">
        <label>Board URL:</label>
        <input type="text" id="boardUrl" placeholder="https://trello.com/b/abc123">
        <button onclick="saveSettings()">Save Settings</button>
    </div>
    <button onclick="fetchChanges()">Refresh Changes</button>
    <div id="content"></div>
    <script>
        const vscode = acquireVsCodeApi();
        
        vscode.postMessage({ command: 'loadSettings' });
        
        function saveSettings() {
            const serverUrl = document.getElementById('serverUrl').value;
            const boardUrl = document.getElementById('boardUrl').value;
            vscode.postMessage({ command: 'saveSettings', serverUrl, boardUrl });
        }
        
        function fetchChanges() {
            document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
            vscode.postMessage({ command: 'fetchChanges' });
        }
        
        window.addEventListener('message', event => {
            const message = event.data;
            const content = document.getElementById('content');
            
            switch (message.command) {
                case 'settingsLoaded':
                    document.getElementById('serverUrl').value = message.serverUrl;
                    document.getElementById('boardUrl').value = message.boardUrl;
                    break;
                case 'updateChanges':
                    displayChanges(message.data);
                    break;
                case 'error':
                    content.innerHTML = '<p class="error">Error: ' + message.message + '</p>';
                    break;
            }
        });
        
        function displayChanges(data) {
            const content = document.getElementById('content');
            if (!data || data.length === 0) {
                content.innerHTML = '<p>No changes found</p>';
                return;
            }
            
            let html = '';
            data.forEach(change => {
                html += '<div class="change-item">' +
                    '<strong>' + (change.type || 'Update') + '</strong>: ' + (change.description || JSON.stringify(change)) +
                    '<br><small>' + (change.timestamp || '') + '</small>' +
                '</div>';
            });
            content.innerHTML = html;
        }
        
        fetchChanges();
    </script>
</body>
</html>`;
    }
}
