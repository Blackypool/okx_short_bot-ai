import logging
from datetime import datetime

class LaTeXReporter:
    def __init__(self):
        self.logger = logging.getLogger('LaTeXReporter')
    
    def generate_daily_report(self, trades: list):
        filename = f"reports/tex/report_{datetime.now().strftime('%Y%m%d')}.tex"
        
        with open(filename, 'w') as f:
            f.write('\\documentclass{article}\n')
            f.write('\\usepackage[utf-8]{inputenc}\n')
            f.write('\\begin{document}\n')
            f.write(f'\\section{{OKX Bot Report {datetime.now().date()}}}\n')
            f.write(f'Total Trades: {len(trades)}\\\\\n')
            f.write(f'Winning: {len([t for t in trades if t.get("pnl", 0) > 0])}\\\\\n')
            f.write(f'Total PnL: {sum([t.get("pnl", 0) for t in trades]):.2f}\n')
            f.write('\\end{document}\n')
        
        self.logger.info(f'📄 LaTeX report: {filename}')
