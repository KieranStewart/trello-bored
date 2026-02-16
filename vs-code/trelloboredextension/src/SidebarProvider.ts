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
            }
        });
    }

    private async _fetchAndDisplayChanges() {
        try {
            const apiUrl = vscode.workspace.getConfiguration('trelloboredextension').get<string>('apiUrl', 'http://localhost:3000/api/changes');
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
        button { padding: 8px 16px; margin-bottom: 16px; cursor: pointer; }
        .change-item { padding: 8px; margin: 8px 0; border-left: 3px solid var(--vscode-button-background); background: var(--vscode-editor-background); }
        .error { color: var(--vscode-errorForeground); }
        .loading { color: var(--vscode-descriptionForeground); }
    </style>
</head>
<body>
    <h2>Trello Board Changes</h2>
    <button onclick="fetchChanges()">Refresh Changes</button>
    <div id="content"></div>
    <script>
        const vscode = acquireVsCodeApi();
        
        function fetchChanges() {
            document.getElementById('content').innerHTML = '<p class="loading">Loading...</p>';
            vscode.postMessage({ command: 'fetchChanges' });
        }
        
        window.addEventListener('message', event => {
            const message = event.data;
            const content = document.getElementById('content');
            
            switch (message.command) {
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
