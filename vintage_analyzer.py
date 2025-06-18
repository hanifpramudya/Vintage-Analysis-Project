"""
Consumer Credit Vintage Analysis Module

This module provides comprehensive vintage analysis functionality for consumer credit portfolios.
It tracks cumulative overdue performance across different booking cohorts and vintage months.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class VintageAnalyzer:
    """
    A comprehensive vintage analysis tool for consumer credit data.
    
    This class handles data loading, processing, and visualization for vintage analysis,
    tracking cumulative overdue days across different booking cohorts.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the VintageAnalyzer.
        
        Args:
            config (Dict, optional): Configuration parameters for analysis
        """
        self.config = config or self._default_config()
        self.credit_df = None
        self.book_df = None
        self.merged_df = None
        self.vintage_table = None
        self.vintage_filled = None
        
    def _default_config(self) -> Dict:
        """Default configuration settings."""
        return {
            'figure_size': (12, 6),
            'turning_point_month': 9,
            'q1_months': ['2024-01-01', '2024-02-01', '2024-03-01'],
            'colors': {
                'primary': 'black',
                'highlight': 'red',
                'grid': 'gray'
            },
            'line_styles': {
                'primary': '--',
                'highlight': '-'
            }
        }
    
    def load_data(self, credit_file: str, book_file: str) -> None:
        """
        Load credit report and book month data from CSV files.
        
        Args:
            credit_file (str): Path to consumer credit report CSV
            book_file (str): Path to consumer book month CSV
        """
        try:
            self.credit_df = pd.read_csv(credit_file)
            self.book_df = pd.read_csv(book_file)
            print(f"✓ Loaded credit data: {len(self.credit_df)} records")
            print(f"✓ Loaded book data: {len(self.book_df)} records")
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Data file not found: {e}")
        except Exception as e:
            raise Exception(f"Error loading data: {e}")
    
    def preprocess_data(self) -> None:
        """
        Merge and preprocess the credit and book month data.
        
        This method:
        1. Merges credit data with book month information
        2. Converts date columns to datetime format
        3. Calculates vintage months
        4. Filters valid records
        5. Sorts data appropriately
        """
        if self.credit_df is None or self.book_df is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        # Merge book month into credit data
        self.merged_df = self.credit_df.merge(
            self.book_df[['ID', 'Book_Month']], 
            on='ID', 
            how='inner'
        )
        
        # Convert months to datetime
        self.merged_df['Month'] = pd.to_datetime(
            self.merged_df['Month'], 
            format='%b %Y'
        )
        self.merged_df['Book_Month'] = pd.to_datetime(
            self.merged_df['Book_Month'], 
            format='%b %Y'
        )
        
        # Calculate vintage month
        self.merged_df['Vintage_Month'] = (
            (self.merged_df['Month'].dt.year - self.merged_df['Book_Month'].dt.year) * 12 +
            (self.merged_df['Month'].dt.month - self.merged_df['Book_Month'].dt.month)
        )
        
        # Filter valid records and sort
        self.merged_df = self.merged_df[self.merged_df['Vintage_Month'] >= 0]
        self.merged_df = self.merged_df.sort_values(by=['ID', 'Vintage_Month'])
        
        print(f"✓ Preprocessed data: {len(self.merged_df)} valid records")
        print(f"✓ Vintage month range: {self.merged_df['Vintage_Month'].min()}-{self.merged_df['Vintage_Month'].max()}")
    
    def compute_ever_bad(self, group: pd.DataFrame) -> pd.DataFrame:
        """
        Compute ever-bad logic: cumulative overdue after first overdue occurrence.
        
        Args:
            group (pd.DataFrame): Customer group data
            
        Returns:
            pd.DataFrame: Group with Ever_Bad column added
        """
        cumulative = 0
        ever_bad_list = []
        
        for overdue in group['Overdue_Days']:
            if overdue > 0 or cumulative > 0:
                cumulative += overdue
            ever_bad_list.append(cumulative)
        
        group['Ever_Bad'] = ever_bad_list
        return group
    
    def calculate_ever_bad_metrics(self) -> None:
        """Apply ever-bad calculation across all customer groups."""
        if self.merged_df is None:
            raise ValueError("Data not preprocessed. Call preprocess_data() first.")
        
        self.merged_df = self.merged_df.groupby('ID').apply(self.compute_ever_bad)
        print("✓ Ever-bad metrics calculated")
    
    def create_vintage_table(self) -> None:
        """Create pivot table for vintage analysis."""
        if self.merged_df is None:
            raise ValueError("Ever-bad metrics not calculated.")
        
        self.vintage_table = self.merged_df.pivot_table(
            index='Book_Month',
            columns='Vintage_Month',
            values='Ever_Bad',
            aggfunc='sum'
        )
        
        # Fill missing values with forward fill
        self.vintage_filled = self.vintage_table.copy().ffill(axis=1)
        
        print(f"✓ Vintage table created: {self.vintage_table.shape}")
    
    def calculate_quarterly_performance(self, quarter_months: List[str]) -> pd.Series:
        """
        Calculate performance for specified quarter months.
        
        Args:
            quarter_months (List[str]): List of month strings in 'YYYY-MM-DD' format
            
        Returns:
            pd.Series: Quarterly performance by vintage month
        """
        if self.vintage_filled is None:
            raise ValueError("Vintage table not created. Call create_vintage_table() first.")
        
        quarter_timestamps = [pd.Timestamp(month) for month in quarter_months]
        available_months = [month for month in quarter_timestamps if month in self.vintage_filled.index]
        
        if not available_months:
            raise ValueError(f"No data available for specified quarter months: {quarter_months}")
        
        return self.vintage_filled.loc[available_months].sum(axis=0)
    
    def plot_quarterly_performance(self, quarter_months: Optional[List[str]] = None) -> None:
        """
        Plot quarterly performance analysis.
        
        Args:
            quarter_months (List[str], optional): Quarter months to analyze
        """
        if quarter_months is None:
            quarter_months = self.config['q1_months']
        
        q_performance = self.calculate_quarterly_performance(quarter_months)
        
        plt.figure(figsize=self.config['figure_size'])
        
        # Main performance line
        plt.plot(
            q_performance.index, 
            q_performance.values, 
            marker='s', 
            linestyle=self.config['line_styles']['primary'], 
            linewidth=2.5, 
            color=self.config['colors']['primary'], 
            label='Q1 Performance'
        )
        
        # Turning point line
        plt.axvline(
            x=self.config['turning_point_month'], 
            color=self.config['colors']['highlight'], 
            linestyle=self.config['line_styles']['highlight'], 
            linewidth=2, 
            alpha=0.7, 
            label='Turning Point'
        )
        
        plt.title('Vintage Analysis - Q1 Performance', fontsize=14, fontweight='bold')
        plt.xlabel('Vintage Month', fontsize=12)
        plt.ylabel('Cumulative Overdue Days', fontsize=12)
        plt.legend(title='Analysis Type')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def plot_monthly_cohorts(self) -> None:
        """Plot individual performance curves for each booking month cohort."""
        if self.vintage_table is None:
            raise ValueError("Vintage table not created. Call create_vintage_table() first.")
        
        plt.figure(figsize=self.config['figure_size'])
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(self.vintage_table.index)))
        
        for i, book_month in enumerate(self.vintage_table.index):
            plt.plot(
                self.vintage_table.columns, 
                self.vintage_table.loc[book_month], 
                marker='o', 
                color=colors[i],
                label=book_month.strftime('%b %Y'),
                linewidth=1.5,
                markersize=4
            )
        
        plt.title('Vintage Analysis - Monthly Cohort Performance', fontsize=14, fontweight='bold')
        plt.xlabel('Vintage Month', fontsize=12)
        plt.ylabel('Cumulative Overdue Days', fontsize=12)
        plt.legend(title='Book Month', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def run_full_analysis(self, credit_file: str, book_file: str) -> None:
        """
        Run complete vintage analysis workflow.
        
        Args:
            credit_file (str): Path to credit report CSV
            book_file (str): Path to book month CSV
        """
        print("🚀 Starting Vintage Analysis...")
        
        # Load and process data
        self.load_data(credit_file, book_file)
        self.preprocess_data()
        self.calculate_ever_bad_metrics()
        self.create_vintage_table()
        
        # Generate visualizations
        print("\n📊 Generating visualizations...")
        self.plot_quarterly_performance()
        self.plot_monthly_cohorts()
        
        print("\n✅ Analysis complete!")
    
    def get_summary_statistics(self) -> Dict:
        """
        Get summary statistics for the vintage analysis.
        
        Returns:
            Dict: Summary statistics including key metrics
        """
        if self.merged_df is None:
            raise ValueError("Analysis not completed. Run analysis first.")
        
        stats = {
            'total_customers': self.merged_df['ID'].nunique(),
            'total_records': len(self.merged_df),
            'vintage_month_range': {
                'min': int(self.merged_df['Vintage_Month'].min()),
                'max': int(self.merged_df['Vintage_Month'].max())
            },
            'book_month_range': {
                'earliest': self.merged_df['Book_Month'].min().strftime('%b %Y'),
                'latest': self.merged_df['Book_Month'].max().strftime('%b %Y')
            },
            'total_overdue_days': int(self.merged_df['Overdue_Days'].sum()),
            'total_ever_bad_days': int(self.merged_df['Ever_Bad'].sum()),
            'customers_with_overdue': int((self.merged_df.groupby('ID')['Overdue_Days'].sum() > 0).sum())
        }
        
        return stats
    
    def export_results(self, output_dir: str = './output/') -> None:
        """
        Export analysis results to CSV files.
        
        Args:
            output_dir (str): Directory to save output files
        """
        import os
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Export vintage table
        if self.vintage_table is not None:
            self.vintage_table.to_csv(f"{output_dir}/vintage_table.csv")
            print(f"✓ Vintage table exported to {output_dir}/vintage_table.csv")
        
        # Export filled vintage table
        if self.vintage_filled is not None:
            self.vintage_filled.to_csv(f"{output_dir}/vintage_table_filled.csv")
            print(f"✓ Filled vintage table exported to {output_dir}/vintage_table_filled.csv")
        
        # Export processed data
        if self.merged_df is not None:
            self.merged_df.to_csv(f"{output_dir}/processed_data.csv", index=False)
            print(f"✓ Processed data exported to {output_dir}/processed_data.csv")


if __name__ == "__main__":
    # Example usage
    analyzer = VintageAnalyzer()
    
    try:
        analyzer.run_full_analysis(
            "consumer_credit_report.csv", 
            "consumer_book_month.csv"
        )
        
        # Print summary statistics
        print("\n📈 Summary Statistics:")
        stats = analyzer.get_summary_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Export results
        analyzer.export_results()
        
    except Exception as e:
        print(f"❌ Error: {e}")
