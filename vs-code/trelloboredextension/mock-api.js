const http = require('http');

const mockData = [
    {
        type: "Card Created",
        description: "New card 'Implement login feature' added to 'To Do' list",
        timestamp: "2024-01-15 10:30 AM"
    },
    {
        type: "Card Moved",
        description: "Card 'Fix bug #123' moved from 'In Progress' to 'Done'",
        timestamp: "2024-01-15 11:45 AM"
    },
    {
        type: "Card Updated",
        description: "Card 'Design homepage' description updated",
        timestamp: "2024-01-15 02:15 PM"
    },
    {
        type: "Card Deleted",
        description: "Card 'Old task' removed from 'Backlog'",
        timestamp: "2024-01-15 03:30 PM"
    }
];

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Access-Control-Allow-Origin', '*');
    
    if (req.url === '/api/changes') {
        res.writeHead(200);
        res.end(JSON.stringify(mockData));
    } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Mock API server running at http://localhost:${PORT}/api/changes`);
});
