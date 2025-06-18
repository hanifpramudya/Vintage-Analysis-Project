#!/usr/bin/env python3
"""
Main execution script for Consumer Credit Vintage Analysis

This script provides a command-line interface for running vintage analysis
on consumer credit data with various configuration options.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import List, Optional
import json

# Add src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vintage_analyzer import VintageAnalyzer


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Consumer Credit Vintage Analysis Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Required arguments
    parser.add_argument(
        '--credit-file', 
        type=str, 
        required=True,
        help='Path to consumer credit report CSV file'
    )
    
    parser.add_argument(
        '--book-file', 
        type=str, 
        required=True,
        help='Path to consumer book month CSV file'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='./output/',
        help='Directory to save output files and plots'
    )
    
    parser.add_argument(
        '--plot-type', 
        type=str, 
        choices=['quarterly', 'monthly', 'both'], 
        default='both',
        help='Type of plots to generate'
    )
    
    parser.add_argument(
        '--turning-point', 
        type=int, 
        default=9,
        help='Vintage month for turning point analysis'
    )
    
    parser.add_argument(
        '--quarter-months', 
        type=str, 
        nargs='+',
        default=['2024-01-01', '2024-02-01', '2024-03-01'],
        help='Months to include in quarterly analysis (YYYY-MM-DD format)'
    )
    
    parser.add_argument(
        '--config-file', 
        type=str,
        help='Path to JSON configuration file'
    )
    
    parser.add_argument(
        '--export-results', 
        action='store_true',
        help='Export analysis results to CSV files'
    )
    
    parser.add_argument(
        '--no-plots', 
        action='store_true',
        help='Skip plot generation (useful for batch processing)'
    )
    
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def load_config(config_file: Optional[str] = None) -> dict:
    """
    Load configuration from file or use defaults.
    
    Args:
        config_file (str, optional): Path to JSON config file
        
    Returns:
        dict: Configuration dictionary
    """
    default_config = {
        'figure_size': [12, 6],
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
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            default_config.update(file_config)
            print(f"✓ Loaded configuration from {config_file}")
        except Exception as e:
            print(f"⚠️  Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration...")
    
    return default_config


def validate_files(credit_file: str, book_file: str) -> bool:
    """
    Validate that input files exist and are readable.
    
    Args:
        credit_file (str): Path to credit file
        book_file (str): Path to book file
        
    Returns:
        bool: True if files are valid
    """
    files_to_check = [
        (credit_file, "Credit report file"),
        (book_file, "Book month file")
    ]
    
    for file_path, file_desc in files_to_check:
        if not os.path.exists(file_path):
            print(f"❌ Error: {file_desc} not found: {file_path}")
            return False
        
        if not os.access(file_path, os.R_OK):
            print(f"❌ Error: {file_desc} is not readable: {file_path}")
            return False
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            print(f"❌ Error: {file_desc} is empty: {file_path}")
            return False
    
    return True


def create_output_directory(output_dir: str) -> bool:
    """
    Create output directory if it doesn't exist.
    
    Args:
        output_dir (str): Path to output directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ Error creating output directory {output_dir}: {e}")
        return False


def print_summary_stats(stats: dict, verbose: bool = False) -> None:
    """
    Print formatted summary statistics.
    
    Args:
        stats (dict): Summary statistics from analyzer
        verbose (bool): Whether to print detailed stats
    """
    print("\n" + "="*50)
    print("📈 VINTAGE ANALYSIS SUMMARY")
    print("="*50)
    
    print(f"Total Customers: {stats['total_customers']:,}")
    print(f"Total Records: {stats['total_records']:,}")
    print(f"Customers with Overdue: {stats['customers_with_overdue']:,}")
    
    if verbose:
        print(f"\nVintage Month Range: {stats['vintage_month_range']['min']}-{stats['vintage_month_range']['max']}")
        print(f"Book Month Range: {stats['book_month_range']['earliest']} to {stats['book_month_range']['latest']}")
        print(f"Total Overdue Days: {stats['total_overdue_days']:,}")
        print(f"Total Ever-Bad Days: {stats['total_ever_bad_days']:,}")
        
        overdue_rate = (stats['customers_with_overdue'] / stats['total_customers']) * 100
        print(f"Overdue Rate: {overdue_rate:.2f}%")


def main():
    """Main execution function."""
    print("🚀 Consumer Credit Vintage Analysis Tool")
    print("="*50)
    
    # Parse arguments
    args = parse_arguments()
    
    # Validate input files
    if not validate_files(args.credit_file, args.book_file):
        sys.exit(1)
    
    # Create output directory
    if not create_output_directory(args.output_dir):
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config_file)
    
    # Update config with command line arguments
    config['turning_point_month'] = args.turning_point
    config['q1_months'] = args.quarter_months
    
    try:
        # Initialize analyzer
        analyzer = VintageAnalyzer(config)
        
        if args.verbose:
            print(f"📂 Processing files:")
            print(f"  Credit file: {args.credit_file}")
            print(f"  Book file: {args.book_file}")
            print(f"  Output directory: {args.output_dir}")
        
        # Load and process data
        print("\n📊 Loading and processing data...")
        analyzer.load_data(args.credit_file, args.book_file)
        analyzer.preprocess_data()
        analyzer.calculate_ever_bad_metrics()
        analyzer.create_vintage_table()
        
        # Generate plots if requested
        if not args.no_plots:
            print("\n🎨 Generating visualizations...")
            
            if args.plot_type in ['quarterly', 'both']:
                print("  → Creating quarterly performance plot...")
                analyzer.plot_quarterly_performance(args.quarter_months)
            
            if args.plot_type in ['monthly', 'both']:
                print("  → Creating monthly cohort plots...")
                analyzer.plot_monthly_cohorts()
        
        # Export results if requested
        if args.export_results:
            print(f"\n💾 Exporting results to {args.output_dir}...")
            analyzer.export_results(args.output_dir)
        
        # Print summary statistics
        stats = analyzer.get_summary_statistics()
        print_summary_stats(stats, args.verbose)
        
        print(f"\n✅ Analysis completed successfully!")
        print(f"📁 Results saved to: {args.output_dir}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
