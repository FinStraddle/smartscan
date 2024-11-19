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
        <div class="stock-card">
            <div class="d-flex justify-content-between align-items-start mb-3">
                <div>
                    <h5 class="stock-name mb-0">${stock.symbol}</h5>
                    <div class="mt-2">
                        <span class="metric-badge bg-light">₹${stock.price.toLocaleString('en-IN')} (${stock.change})</span>
                    </div>
                </div>
                <span class="badge ${signalClass}">${stock.signal}</span>
            </div>
            
            <div class="chart-container mb-3">
                <img src="charts/${stock.symbol}_technical_analysis.png" alt="${stock.symbol} Chart" class="img-fluid rounded">
            </div>
            
            <div class="metrics-grid">
                <div class="metric-item">
                    <small class="text-muted d-block mb-1">RSI</small>
                    <div class="metric-badge ${getRSIClass(stock.rsi)}">${stock.rsi}</div>
                </div>
                <div class="metric-item">
                    <small class="text-muted d-block mb-1">MACD</small>
                    <div class="metric-badge ${getMACDClass(stock.macd)}">${stock.macd}</div>
                </div>
                <div class="metric-item">
                    <small class="text-muted d-block mb-1">SMA20</small>
                    <div class="metric-badge bg-light">₹${stock.sma20}</div>
                </div>
                <div class="metric-item">
                    <small class="text-muted d-block mb-1">SMA50</small>
                    <div class="metric-badge bg-light">₹${stock.sma50}</div>
                </div>
                <div class="metric-item">
                    <small class="text-muted d-block mb-1">Volume</small>
                    <div class="metric-badge bg-light">${stock.volume}</div>
                </div>
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
    let currentStock = null;
    
    // Split the markdown into lines and process each line
    const lines = markdown.split('\n');
    
    lines.forEach(line => {
        // Check for stock symbol
        const symbolMatch = line.match(/\| \*\*(.*?)\.NS\*\*/);
        if (symbolMatch) {
            if (currentStock) {
                stocks.push(currentStock);
            }
            currentStock = {
                symbol: symbolMatch[1] + '.NS',
                signal: '',
                price: 0,
                change: '',
                rsi: 0,
                macd: 0,
                sma20: '',
                sma50: '',
                volume: ''
            };
        }
        
        if (currentStock) {
            // Extract signal
            if (line.includes('Signal:')) {
                const signalMatch = line.match(/Signal: ([^<]+)/);
                if (signalMatch) {
                    currentStock.signal = signalMatch[1].trim();
                }
            }
            
            // Extract price and change
            if (line.includes('Price:')) {
                const priceMatch = line.match(/Price: ₹([\d,]+\.?\d*) \(([-+]?\d+\.\d+%)\)/);
                if (priceMatch) {
                    currentStock.price = parseFloat(priceMatch[1].replace(',', ''));
                    currentStock.change = priceMatch[2];
                }
            }
            
            // Extract RSI
            if (line.includes('RSI:')) {
                const rsiMatch = line.match(/RSI: ([\d.]+)/);
                if (rsiMatch) {
                    currentStock.rsi = parseFloat(rsiMatch[1]);
                }
            }
            
            // Extract MACD
            if (line.includes('MACD:')) {
                const macdMatch = line.match(/MACD: ([-\d.]+)/);
                if (macdMatch) {
                    currentStock.macd = parseFloat(macdMatch[1]);
                }
            }
            
            // Extract SMAs
            if (line.includes('SMA20:')) {
                const sma20Match = line.match(/SMA20: ₹([\d,]+\.?\d*)/);
                if (sma20Match) {
                    currentStock.sma20 = sma20Match[1];
                }
            }
            if (line.includes('SMA50:')) {
                const sma50Match = line.match(/SMA50: ₹([\d,]+\.?\d*)/);
                if (sma50Match) {
                    currentStock.sma50 = sma50Match[1];
                }
            }
            
            // Extract Volume
            if (line.includes('Volume:')) {
                const volumeMatch = line.match(/Volume: ([^|]+)/);
                if (volumeMatch) {
                    currentStock.volume = volumeMatch[1].trim();
                }
            }
        }
    });
    
    // Don't forget to add the last stock
    if (currentStock) {
        stocks.push(currentStock);
    }
    
    return stocks;
}

// Load and process the markdown file
async function loadStockData() {
    try {
        const response = await fetch('reports/nifty50_analysis-2024-11-18.md');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const markdown = await response.text();
        const stocks = parseMarkdownToStocks(markdown);
        
        if (stocks.length === 0) {
            console.error('No stocks were parsed from the markdown file');
            document.getElementById('stockAnalysis').innerHTML = '<div class="alert alert-danger">No stocks found in the data</div>';
            return;
        }
        
        const container = document.getElementById('stockAnalysis');
        container.innerHTML = ''; // Clear existing content
        stocks.forEach(stock => {
            const card = createStockCard(stock);
            container.appendChild(card);
        });
        
        console.log(`Successfully loaded ${stocks.length} stocks`);
        
        // Initialize search functionality
        document.getElementById('searchStocks').addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            const stockCards = document.querySelectorAll('.col-md-6');
            
            stockCards.forEach(card => {
                const stockName = card.querySelector('.stock-name').textContent.toLowerCase();
                const parentCard = card;
                parentCard.style.display = stockName.includes(searchTerm) ? '' : 'none';
            });
        });

        // Initialize signal filtering
        document.getElementById('signalFilter').addEventListener('change', function(e) {
            const signal = e.target.value.toLowerCase();
            const stockCards = document.querySelectorAll('.col-md-6');
            
            stockCards.forEach(card => {
                const cardSignal = card.getAttribute('data-signal');
                if (signal === 'all' || cardSignal.includes(signal)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });

        // Initialize sorting
        document.querySelectorAll('[data-sort]').forEach(button => {
            button.addEventListener('click', function() {
                const criterion = this.getAttribute('data-sort');
                const stockCards = Array.from(document.querySelectorAll('.col-md-6'));
                
                stockCards.sort((a, b) => {
                    let aValue = a.getAttribute(`data-${criterion}`);
                    let bValue = b.getAttribute(`data-${criterion}`);
                    
                    if (criterion === 'price' || criterion === 'rsi') {
                        return parseFloat(bValue) - parseFloat(aValue);
                    }
                    return bValue.localeCompare(aValue);
                });
                
                const container = document.getElementById('stockAnalysis');
                container.innerHTML = '';
                stockCards.forEach(card => container.appendChild(card));
            });
        });
        
    } catch (error) {
        console.error('Error loading stock data:', error);
        document.getElementById('stockAnalysis').innerHTML = `<div class="alert alert-danger">Error loading stock data: ${error.message}</div>`;
    }
}

// Initialize when the document is loaded
document.addEventListener('DOMContentLoaded', loadStockData);
