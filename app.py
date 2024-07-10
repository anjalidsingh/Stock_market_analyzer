from flask import Flask, render_template
import sqlite3
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def get_stock_data():
    conn = sqlite3.connect('indian_stock_data.db')
    query = """
    SELECT 
        substr(name, 1, instr(name, '_') - 1) as symbol,
        avg(Daily_Return) as avg_daily_return,
        max(Total_Return) as total_return,
        max(Volatility) as volatility,
        max(Sharpe_Ratio) as sharpe_ratio
    FROM (
        SELECT name FROM sqlite_master WHERE type='table'
    )
    JOIN (
        SELECT 'TATAMOTORS_data' as name, Daily_Return, Total_Return, Volatility, Sharpe_Ratio FROM TATAMOTORS_data
        UNION ALL
        SELECT 'TATASTEEL_data' as name, Daily_Return, Total_Return, Volatility, Sharpe_Ratio FROM TATASTEEL_data
        UNION ALL
        SELECT 'TATAPOWER_data' as name, Daily_Return, Total_Return, Volatility, Sharpe_Ratio FROM TATAPOWER_data
    )
    USING (name)
    GROUP BY symbol
    """
    results = pd.read_sql_query(query, conn)
    conn.close()
    return results

def create_plot():
    results = get_stock_data()
    metrics = ['avg_daily_return', 'total_return', 'volatility', 'sharpe_ratio']
    
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle('Indian Stock Metrics Comparison', fontsize=16)

    for i, metric in enumerate(metrics):
        ax = axs[i//2, i%2]
        ax.bar(results['symbol'], results[metric])
        ax.set_title(metric.replace('_', ' ').title(), fontsize=10)
        ax.set_xlabel('Stock Symbol', fontsize=8)
        ax.set_ylabel('Value', fontsize=8)
        ax.tick_params(axis='both', which='major', labelsize=8)

    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100)
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    return plot_url

@app.route('/')
def index():
    results = get_stock_data()
    plot_url = create_plot()
    return render_template('index.html', tables=[results.to_html(classes='data')], titles=results.columns.values, plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)