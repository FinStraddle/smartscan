// Function to create a stock card
function createStockCard(stock) {
    const signalClass = stock.signal.toLowerCase().includes('buy') ? 'signal-buy' : 
                       stock.signal.toLowerCase().includes('sell') ? 'signal-sell' : 'signal-neutral';
    
    const card = document.createElement('div');
    card.className = 'col-md-6 col-lg-4 mb-4';
    card.setAttribute('data-signal', stock.signal.toLowerCase());
    card.setAttribute('data-price', stock.price);
    card.setAttribute('data-rsi', stock.rsi);
    
    card.innerHTML = `
        <div class="stock-card h-100">
            <div class="d-flex justify-content-between align-items-start">
                <h5 class="stock-name">${stock.symbol}</h5>
                <span class="badge ${signalClass}">${stock.signal}</span>
            </div>
            <div class="mb-3">
                <span class="metric-badge bg-light">₹${stock.price} (${stock.change})</span>
            </div>
            <div class="row mb-3">
                <div class="col">
                    <small class="text-muted">RSI</small>
                    <div class="metric-badge ${getRSIClass(stock.rsi)}">${stock.rsi}</div>
                </div>
                <div class="col">
                    <small class="text-muted">MACD</small>
                    <div class="metric-badge ${getMACDClass(stock.macd)}">${stock.macd}</div>
                </div>
            </div>
            <div class="chart-container">
                <img src="charts/${stock.symbol}_technical_analysis.png" alt="${stock.symbol} Chart" class="img-fluid">
            </div>
            <div class="mt-3">
                <small class="text-muted">Moving Averages</small>
                <div class="d-flex gap-2 mt-1">
                    <span class="metric-badge bg-light">SMA20: ${stock.sma20}</span>
                    <span class="metric-badge bg-light">SMA50: ${stock.sma50}</span>
                </div>
            </div>
            <div class="mt-2">
                <small class="text-muted">Volume</small>
                <div class="metric-badge bg-light">${stock.volume}</div>
            </div>
        </div>
    `;
    
    return card;
}

// Helper functions for styling
function getRSIClass(rsi) {
    if (rsi > 70) return 'bg-danger text-white';
    if (rsi < 30) return 'bg-warning';
    return 'bg-success text-white';
}

function getMACDClass(macd) {
    return macd > 0 ? 'bg-success text-white' : 'bg-danger text-white';
}

// Parse markdown content to extract stock data
function parseMarkdownToStocks(markdown) {
    const stocks = [];
    const lines = markdown.split('\n');
    let currentStock = null;

    lines.forEach(line => {
        if (line.startsWith('| **')) {
            if (currentStock) stocks.push(currentStock);
            currentStock = {
                symbol: line.match(/\*\*(.*?)\*\*/)[1],
                signal: '',
                price: 0,
                change: '',
                rsi: 0,
                macd: 0,
                sma20: '',
                sma50: '',
                volume: ''
            };
        } else if (currentStock) {
            if (line.includes('Signal:')) {
                currentStock.signal = line.match(/Signal: (.*?)<br>/)[1];
            } else if (line.includes('Price:')) {
                const priceMatch = line.match(/Price: ₹([\d,]+\.?\d*) \((.*?)\)/);
                currentStock.price = parseFloat(priceMatch[1].replace(',', ''));
                currentStock.change = priceMatch[2];
            } else if (line.includes('RSI:')) {
                currentStock.rsi = parseFloat(line.match(/RSI: ([\d.]+)/)[1]);
            } else if (line.includes('MACD:')) {
                currentStock.macd = parseFloat(line.match(/MACD: ([-\d.]+)/)[1]);
            } else if (line.includes('SMA20:')) {
                currentStock.sma20 = line.match(/SMA20: (.*?)<br>/)[1];
            } else if (line.includes('SMA50:')) {
                currentStock.sma50 = line.match(/SMA50: (.*?)<br>/)[1];
            } else if (line.includes('Volume:')) {
                currentStock.volume = line.match(/Volume: (.*?) \|/)[1];
            }
        }
    });

    if (currentStock) stocks.push(currentStock);
    return stocks;
}

// Load and process the markdown file
async function loadStockData() {
    try {
        const response = await fetch('../reports/nifty50_analysis-2024-11-18.md');
        const markdown = await response.text();
        const stocks = parseMarkdownToStocks(markdown);
        
        const container = document.getElementById('stockAnalysis');
        stocks.forEach(stock => {
            const card = createStockCard(stock);
            container.appendChild(card);
        });
    } catch (error) {
        console.error('Error loading stock data:', error);
    }
}
